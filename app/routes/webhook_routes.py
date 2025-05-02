from fastapi import APIRouter, Request, Depends, HTTPException, status
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
from ..db.session import get_db
from ..repositories.conversation_repository import ConversationRepository
from ..core.dependencies import (
    get_dialog360_service,
    get_current_business,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.message_cache import MessageCache

router = APIRouter()


@router.post("/incoming-whatsapp")
async def whatsapp_wbhook(
    request: Request,
    dialog360_service: Dialog360Service = Depends(get_dialog360_service),
    db: Session = Depends(get_db),
):
    """
    Webhook to receive WhatsApp messages via WhatsApp Business API.
    Responds with the processed message from get_response_from_gpt.
    """
    # Parse incoming JSON payload
    data = await request.json()
    
    try:
        # Only use this for debugging, otherwise it will fill up logs
        # print(f"Data =============================================>> {data}")
        
        # Check object first - should be whatsapp_business_account
        if data.get('object') != 'whatsapp_business_account':
            logging.info(f"Ignoring non-WhatsApp webhook object: {data.get('object')}")
            return JSONResponse(content={"status": "success"}, status_code=200)
            
        # Extract the key components in a simplified way
        entry = data.get('entry', [])
        if not entry or not entry[0].get('changes', []):
            logging.info("Ignoring webhook with empty entry or changes")
            return JSONResponse(content={"status": "success"}, status_code=200)
            
        # Get the value field that contains message data
        value = entry[0].get('changes', [])[0].get('value', {})
        
        # Verify this is a message event (should have messages array)
        messages = value.get('messages', [])
        if not messages:
            logging.info("Ignoring webhook without messages field")
            return JSONResponse(content={"status": "success"}, status_code=200)
        
        # Get the first message
        message = messages[0]
        message_type = message.get('type')
        message_id = message.get('id', '')
        
        # Only process text messages
        if message_type != 'text':
            logging.info(f"Ignoring non-text message of type: {message_type}")
            return JSONResponse(content={"status": "success"}, status_code=200)
        
        # Get the contact info
        contacts = value.get('contacts', [])
        if not contacts:
            logging.error("No contact information in the webhook payload")
            return JSONResponse(content={"status": "success"}, status_code=200)
        
        # Extract the key information we need
        wa_id = contacts[0].get('wa_id')
        sender_number = message.get('from')
        number = wa_id or sender_number
        
        if not number:
            logging.error("No sender number found in the request")
            return JSONResponse(content={"status": "success"}, status_code=200)
            
        # Format the number
        number = "".join(filter(str.isdigit, number))
        
        # Get the message text
        incoming_msg = message.get('text', {}).get('body', '').lower()
        if not incoming_msg:
            logging.error("No message text found in the request")
            return JSONResponse(content={"status": "success"}, status_code=200)
        
        # CRITICAL: Check if we've already processed this message
        # Use a simple in-memory cache to prevent duplicates
        message_cache = MessageCache.get_instance()
        
        # Check if we've already processed this message ID
        if message_cache.is_processed(message_id):
            logging.info(f"Skipping already processed message ID: {message_id}")
            return JSONResponse(content={"status": "success"}, status_code=200)
            
        # Mark this message as processed
        message_cache.mark_as_processed(message_id)
        
        profile_name = contacts[0].get('profile', {}).get('name', '') if contacts else ''
        logging.info(f"Processing message from {number} (contact: {profile_name}): {incoming_msg}")
        
        # Process the message with your AI assistant
        # Using the tools_wrapper_util function directly without instantiating AssistantManager
        response = get_response_from_gpt(incoming_msg, number)
        response = format_response(response)
        
        # Send the response
        logging.info(f"Sending response to {number}: {response}")
        resp = dialog360_service.send_whatsapp(number, response)
        
        return JSONResponse(content={"status": "success"}, status_code=200)
        
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(content={"status": "success"}, status_code=200)



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
