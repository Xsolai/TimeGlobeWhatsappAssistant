from fastapi import APIRouter, Request, Depends, HTTPException, status, BackgroundTasks
from app.chat_agent import ChatAgent
from ..services.dialog360_service import Dialog360Service
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
    get_current_business,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.message_cache import MessageCache
from app.utils.message_queue import MessageQueue

router = APIRouter()

@router.post("/incoming-whatsapp")
async def whatsapp_wbhook(
    request: Request,
):
    """
    Webhook to receive WhatsApp messages via WhatsApp Business API.
    Responds immediately and adds the message to a processing queue.
    """
    start_time = time.time()
    
    try:
        # Parse incoming JSON payload
        data = await request.json()
        
        # Log webhook receipt time
        receipt_time = time.time()
        time_to_parse = (receipt_time - start_time) * 1000
        logging.info(f"⏱️ Webhook received at {receipt_time:.3f} - JSON parsing took {time_to_parse:.2f}ms")
        
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


async def process_webhook_data_with_dependencies(data: dict):
    """This function is kept for backward compatibility but no longer used."""
    # Create database session and dialog360 service inside the background task
    db = SessionLocal()
    try:
        dialog360_service = Dialog360Service(db)
        # Process the webhook data with created dependencies
        await process_webhook_data(data, dialog360_service)
    except Exception as e:
        logging.error(f"Error in process_webhook_data_with_dependencies: {str(e)}")
    finally:
        # Make sure to close the DB session
        db.close()


async def process_webhook_data(data: dict, dialog360_service: Dialog360Service):
    """Process the webhook data in the background."""
    start_process_time = time.time()
    
    try:
        # Only use this for debugging, otherwise it will fill up logs
        logging.info(f"Processing webhook - Timestamp: {data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('timestamp', 'unknown')}")
        
        # Check object first - should be whatsapp_business_account
        if data.get('object') != 'whatsapp_business_account':
            logging.info(f"Ignoring non-WhatsApp webhook object: {data.get('object')}")
            return
            
        # Extract the key components in a simplified way
        entry = data.get('entry', [])
        if not entry or not entry[0].get('changes', []):
            logging.info("Ignoring webhook with empty entry or changes")
            return
            
        # Get the value field that contains message data
        value = entry[0].get('changes', [])[0].get('value', {})
        
        # Extract the display_phone_number from metadata
        metadata = value.get('metadata', {})
        business_phone_number = metadata.get('display_phone_number')
        logging.info(f"Business phone number from webhook: {business_phone_number}")
        
        # Verify this is a message event (should have messages array)
        messages = value.get('messages', [])
        if not messages:
            logging.info("Ignoring webhook without messages field")
            return
        
        # Get the first message
        message = messages[0]
        message_type = message.get('type')
        message_id = message.get('id', '')
        timestamp = message.get('timestamp', '')
        
        logging.info(f"Processing webhook - ID: {message_id}, Type: {message_type}, Timestamp: {timestamp}")
        
        # Only process text messages
        if message_type != 'text':
            logging.info(f"Ignoring non-text message of type: {message_type}")
            return
        
        # Get the contact info
        contacts = value.get('contacts', [])
        if not contacts:
            logging.error("No contact information in the webhook payload")
            return
        
        # Extract the key information we need
        wa_id = contacts[0].get('wa_id')
        sender_number = message.get('from')
        number = wa_id or sender_number
        
        if not number:
            logging.error("No sender number found in the request")
            return
            
        # Format the number
        number = "".join(filter(str.isdigit, number))
        
        # Get the message text
        incoming_msg = message.get('text', {}).get('body', '').lower()
        if not incoming_msg:
            logging.error("No message text found in the request")
            return
        
        # CRITICAL: Check if we've already processed this message
        # Use a simple in-memory cache to prevent duplicates
        message_cache = MessageCache.get_instance()
        
        # Check if we've already processed this message ID
        if message_cache.is_processed(message_id):
            logging.warning(f"DUPLICATE MESSAGE DETECTED - Skipping already processed message ID: {message_id}")
            return
        
        # Get profile information
        profile_name = contacts[0].get('profile', {}).get('name', '') if contacts else ''
        logging.info(f"Message from {number} (contact: {profile_name}): '{incoming_msg}'")
        
        # Mark this message as processed BEFORE processing to prevent race conditions
        message_cache.mark_as_processed(message_id)
        
        # Store the business phone number in the conversation context or user session
        # Here we're using MessageCache to store this information 
        message_cache.set_business_phone(number, business_phone_number)
        
        # Log preparation time before message processing
        prep_time = time.time()
        prep_duration = (prep_time - start_process_time) * 1000  # milliseconds
        logging.info(f"⏱️ Webhook data preparation took {prep_duration:.2f}ms for message ID: {message_id}")
        
        # Process the message and send a response
        await process_message(number, incoming_msg, message_id, dialog360_service)
        
        # Total processing time
        end_time = time.time()
        total_duration = (end_time - start_process_time) * 1000  # milliseconds
        logging.info(f"⏱️ Total webhook background processing time: {total_duration:.2f}ms for message ID: {message_id}")
        
    except Exception as e:
        # Log error with timing information
        error_time = time.time()
        total_duration = (error_time - start_process_time) * 1000  # milliseconds
        logging.error(f"Error processing webhook data after {total_duration:.2f}ms: {str(e)}")


async def process_message(number: str, incoming_msg: str, message_id: str, dialog360_service: Dialog360Service):
    """Process a WhatsApp message in the background and send the response."""
    start_process_time = time.time()
    try:
        # Process the message with your AI assistant
        logging.info(f"Generating response for message ID: {message_id} from user: {number}")
        gpt_start_time = time.time()
        response = get_response_from_gpt(incoming_msg, number)
        gpt_end_time = time.time()
        gpt_duration = (gpt_end_time - gpt_start_time) * 1000  # milliseconds
        logging.info(f"⏱️ GPT response generation took {gpt_duration:.2f}ms for message ID: {message_id}")
        
        response = format_response(response)
        
        # Send the response
        send_start_time = time.time()
        logging.info(f"Sending response to {number}: '{response[:50]}...' (truncated)")
        # Retrieve the business phone number associated with this user
        message_cache = MessageCache.get_instance()
        business_phone = message_cache.get_business_phone(number)

        resp = dialog360_service.send_whatsapp(number, response, business_phone)
        send_end_time = time.time()
        send_duration = (send_end_time - send_start_time) * 1000  # milliseconds
        
        # Total processing time
        total_duration = (send_end_time - start_process_time) * 1000  # milliseconds
        logging.info(f"⏱️ WhatsApp API send took {send_duration:.2f}ms for message ID: {message_id}")
        logging.info(f"⏱️ Total message processing time: {total_duration:.2f}ms for message ID: {message_id}")
        
        # Log successful processing
        logging.info(f"Successfully processed message ID: {message_id}")
    except Exception as e:
        # Log error with timing information
        error_time = time.time()
        total_duration = (error_time - start_process_time) * 1000  # milliseconds
        logging.error(f"Error in background processing of message {message_id} after {total_duration:.2f}ms: {str(e)}")


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
