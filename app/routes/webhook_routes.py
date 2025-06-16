from fastapi import APIRouter, Request, Depends, HTTPException, status, BackgroundTasks
from app.chat_agent import ChatAgent
from ..services.dialog360_service import Dialog360Service
from ..services.whatsapp_business_service import WhatsAppBusinessService
from ..schemas.dialog360_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
from ..core.config import settings
from ..models.business_model import Business
from ..utils.tools_wrapper_util import get_response_from_gpt
from ..utils.tools_wrapper_util import format_response
import logging
import time
from ..db.session import get_db, SessionLocal
from ..repositories.conversation_repository import ConversationRepository
from ..core.dependencies import (
    get_dialog360_service,
    get_whatsapp_business_service,
    get_current_business,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.message_cache import MessageCache
from app.utils.message_queue import MessageQueue

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    whatsapp_service: WhatsAppBusinessService = Depends(get_whatsapp_business_service)
):
    """
    Webhook verification endpoint for WhatsApp Business API.
    Facebook/Meta calls this endpoint to verify your webhook.
    """
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logging.info(f"Webhook verification request - Mode: {mode}, Token: {token}")
        
        # Check if this is a webhook verification request
        if mode == "subscribe" and token and challenge:
            # Verify the token using the WhatsApp Business service
            verified_challenge = whatsapp_service.verify_webhook(token, challenge)
            logging.info("Webhook verification successful")
            return int(verified_challenge)
        else:
            logging.error("Webhook verification failed - missing parameters")
            raise HTTPException(status_code=403, detail="Webhook verification failed")
            
    except Exception as e:
        logging.error(f"Error in webhook verification: {str(e)}")
        raise HTTPException(status_code=403, detail="Webhook verification failed")

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
):
    """
    Main webhook endpoint for receiving WhatsApp messages via Meta's WhatsApp Business API.
    This replaces the old Dialog360 webhook.
    """
    start_time = time.time()
    
    try:
        # Parse incoming JSON payload
        data = await request.json()
        
        # Log webhook receipt time
        receipt_time = time.time()
        time_to_parse = (receipt_time - start_time) * 1000
        logging.info(f"⏱️ WhatsApp Business API webhook received at {receipt_time:.3f} - JSON parsing took {time_to_parse:.2f}ms")
        
        # Add message to the processing queue
        message_queue = MessageQueue.get_instance()
        message_queue.enqueue_message(data)
        
        # Calculate response time
        response_time = time.time()
        time_gap = (response_time - start_time) * 1000  # Convert to milliseconds
        logging.info(f"⏱️ Webhook response time: {time_gap:.2f}ms - Responded at {response_time:.3f}")
        
        # Return success immediately before any processing
        return JSONResponse(content={"status": "success"}, status_code=200)
    except Exception as e:
        # Calculate error response time
        error_time = time.time()
        time_gap = (error_time - start_time) * 1000  # Convert to milliseconds
        logging.error(f"Error in webhook handler: {str(e)} - Response time: {time_gap:.2f}ms")
        # Still return 200 to prevent WhatsApp from retrying
        return JSONResponse(content={"status": "success"}, status_code=200)

@router.post("/incoming-whatsapp")
async def whatsapp_dialog360_webhook(
    request: Request,
):
    """
    DEPRECATED: Legacy webhook for Dialog360 integration.
    Maintained for backward compatibility during migration.
    Use /webhook endpoint for new WhatsApp Business API integration.
    """
    start_time = time.time()
    
    try:
        # Parse incoming JSON payload
        data = await request.json()
        
        # Log webhook receipt time
        receipt_time = time.time()
        time_to_parse = (receipt_time - start_time) * 1000
        logging.info(f"⏱️ [DEPRECATED] Dialog360 webhook received at {receipt_time:.3f} - JSON parsing took {time_to_parse:.2f}ms")
        
        # Add message to the processing queue
        message_queue = MessageQueue.get_instance()
        message_queue.enqueue_message(data)
        
        # Calculate response time
        response_time = time.time()
        time_gap = (response_time - start_time) * 1000  # Convert to milliseconds
        logging.info(f"⏱️ Dialog360 webhook response time: {time_gap:.2f}ms - Responded at {response_time:.3f}")
        
        # Return success immediately before any processing
        return JSONResponse(content={"status": "success"}, status_code=200)
    except Exception as e:
        # Calculate error response time
        error_time = time.time()
        time_gap = (error_time - start_time) * 1000  # Convert to milliseconds
        logging.error(f"Error in Dialog360 webhook handler: {str(e)} - Response time: {time_gap:.2f}ms")
        # Still return 200 to prevent WhatsApp from retrying
        return JSONResponse(content={"status": "success"}, status_code=200)

async def process_webhook_data(data: dict, service):
    """Process the webhook data in the background - supports both Dialog360 and WhatsApp Business API."""
    start_process_time = time.time()
    
    try:
        # Detect webhook format and process accordingly
        if data.get('object') == 'whatsapp_business_account':
            # New WhatsApp Business API format
            await process_whatsapp_business_webhook(data, service)
        elif 'entry' in data and data.get('entry', [{}])[0].get('changes'):
            # Could be Dialog360 format, try to process
            await process_dialog360_webhook(data, service)
        else:
            logging.info("Unknown webhook format, attempting WhatsApp Business API processing")
            await process_whatsapp_business_webhook(data, service)
            
    except Exception as e:
        # Log error with timing information
        error_time = time.time()
        total_duration = (error_time - start_process_time) * 1000  # milliseconds
        logging.error(f"Error processing webhook data after {total_duration:.2f}ms: {str(e)}")

async def process_whatsapp_business_webhook(data: dict, service):
    """Process WhatsApp Business API webhook format."""
    start_process_time = time.time()
    
    try:
        logging.info(f"Processing WhatsApp Business API webhook")
        
        # Extract entry data
        entries = data.get('entry', [])
        if not entries:
            logging.info("No entries found in webhook data")
            return
        
        for entry in entries:
            # Get changes
            changes = entry.get('changes', [])
            if not changes:
                continue
                
            for change in changes:
                value = change.get('value', {})
                
                # Extract metadata
                metadata = value.get('metadata', {})
                business_phone_number = metadata.get('display_phone_number')
                phone_number_id = metadata.get('phone_number_id')
                
                logging.info(f"Business phone: {business_phone_number}, Phone ID: {phone_number_id}")
                
                # Process messages
                messages = value.get('messages', [])
                if not messages:
                    logging.info("No messages in webhook data")
                    continue
                
                for message in messages:
                    await process_whatsapp_message(message, value, business_phone_number, service)
                    
    except Exception as e:
        logging.error(f"Error processing WhatsApp Business API webhook: {str(e)}")

async def process_dialog360_webhook(data: dict, service):
    """Process Dialog360 webhook format (DEPRECATED)."""
    logging.warning("Processing DEPRECATED Dialog360 webhook format")
    
    # Use the original processing logic for Dialog360
    await process_webhook_data_original(data, service)

async def process_whatsapp_message(message: dict, value: dict, business_phone_number: str, service):
    """Process individual WhatsApp message."""
    try:
        message_type = message.get('type')
        message_id = message.get('id', '')
        timestamp = message.get('timestamp', '')
        sender_number = message.get('from')
        
        logging.info(f"Processing message - ID: {message_id}, Type: {message_type}, From: {sender_number}")
        
        # Only process text messages
        if message_type != 'text':
            logging.info(f"Ignoring non-text message of type: {message_type}")
            return
        
        # Get message text
        text_content = message.get('text', {})
        message_body = text_content.get('body', '')
        
        if not message_body:
            logging.error("No message text found")
            return
        
        # Get contact info
        contacts = value.get('contacts', [])
        profile_name = ''
        if contacts:
            profile = contacts[0].get('profile', {})
            profile_name = profile.get('name', '')
        
        # Format phone number
        if not sender_number:
            logging.error("No sender number found")
            return
            
        formatted_number = "".join(filter(str.isdigit, sender_number))
        
        # Check for duplicate messages
        message_cache = MessageCache.get_instance()
        if message_cache.is_processed(message_id):
            logging.warning(f"DUPLICATE MESSAGE DETECTED - Skipping message ID: {message_id}")
            return
        
        # Mark as processed
        message_cache.mark_as_processed(message_id)
        message_cache.set_business_phone(formatted_number, business_phone_number)
        
        logging.info(f"Message from {formatted_number} (contact: {profile_name}): '{message_body}'")
        
        # Process the message
        await process_message_universal(formatted_number, message_body.lower(), message_id, service)
        
    except Exception as e:
        logging.error(f"Error processing WhatsApp message: {str(e)}")

async def process_message_universal(number: str, incoming_msg: str, message_id: str, service):
    """Universal message processor that works with both Dialog360 and WhatsApp Business API services."""
    start_process_time = time.time()
    try:
        # Process the message with your AI assistant
        logging.info(f"Generating response for message ID: {message_id} from user: {number}")
        gpt_start_time = time.time()
        response = get_response_from_gpt(incoming_msg, number)
        
        gpt_end_time = time.time()
        gpt_duration = (gpt_end_time - gpt_start_time) * 1000  # milliseconds
        logging.info(f"⏱️ GPT response generation took {gpt_duration:.2f}ms for message ID: {message_id}")
        
        if response:
            # Format the response
            formatted_response = format_response(response)
            
            # Get the business phone number for this user
            message_cache = MessageCache.get_instance()
            business_phone = message_cache.get_business_phone(number)
            
            if not business_phone:
                logging.error(f"No business phone number found for user {number}")
                return
            
            # Send the response using the appropriate service
            if hasattr(service, 'send_message'):
                # New WhatsApp Business API service
                resp = service.send_message(number, formatted_response, business_phone)
            else:
                # Legacy Dialog360 service
                resp = service.send_whatsapp(number, formatted_response, business_phone)
            
            # Total processing time
            end_time = time.time()
            total_duration = (end_time - start_process_time) * 1000  # milliseconds
            logging.info(f"⏱️ Total message processing time: {total_duration:.2f}ms for message ID: {message_id}")
        else:
            logging.error(f"No response generated for message ID: {message_id}")
            
    except Exception as e:
        logging.error(f"Error in message processing for message ID {message_id}: {str(e)}")

# Keep the original method for backward compatibility
async def process_webhook_data_original(data: dict, dialog360_service: Dialog360Service):
    """Original Dialog360 webhook processing logic (DEPRECATED)."""

@router.delete("/clear-chat-history/{mobile_number}", status_code=status.HTTP_200_OK, response_class=JSONResponse)
async def clear_chat_history(
    mobile_number: str,
    db: Session = Depends(get_db),
    current_business: Business = Depends(get_current_business),
):
    """Clear the conversation history for a user"""
    try:
        conversation_repo = ConversationRepository(db)
        success = conversation_repo.delete_conversation_history(mobile_number)
        
        if success:
            return JSONResponse(
                content={"status": "success", "message": f"Chat history cleared for {mobile_number}"},
                status_code=200,
            )
        else:
            return JSONResponse(
                content={"status": "success", "message": "No chat history found to clear"},
                status_code=200,
            )
    except Exception as e:
        logging.error(f"Error clearing chat history: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500,
        )
