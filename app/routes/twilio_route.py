from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
import logging
from functools import lru_cache
from typing import Optional

from app.agent import AssistantManager
from ..services.twilio_service import TwilioService
from ..schemas.twilio_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
from ..core.config import settings
from ..schemas.auth import User
from ..utils.tools_wrapper_util import get_response_from_gpt, format_response
from ..db.session import get_db
from ..core.dependencies import (
    get_twilio_service,
    validate_twilio_request,
    get_current_user,
)

router = APIRouter()

# Cache the AssistantManager instance
@lru_cache(maxsize=1)
def get_cached_assistant_manager(db: Session) -> AssistantManager:
    return AssistantManager(settings.OPENAI_API_KEY, settings.OPENAI_ASSISTANT_ID, db)

# Cache the TwilioService instance
@lru_cache(maxsize=1)
def get_cached_twilio_service(db: Session) -> TwilioService:
    return TwilioService(db)

@router.post("/incoming-whatsapp")
async def whatsapp_wbhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Webhook to receive WhatsApp messages via Twilio.
    Responds with the processed message from get_response_from_gpt.
    """
    # Validate request early
    await validate_twilio_request(request)
    
    # Get form data
    form_data = await request.form()
    incoming_msg = form_data.get("Body", "").lower()
    sender_number = form_data.get("From", "")
    
    if not incoming_msg or not sender_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required message or sender information"
        )
    
    # Clean sender number
    number = "".join(filter(str.isdigit, sender_number))
    logging.info(f"Incoming message from {sender_number}: {incoming_msg}")
    
    try:
        # Get cached service instances
        twilio_service = get_cached_twilio_service(db)
        assistant_manager = get_cached_assistant_manager(db)
        
        # Process message
        response = get_response_from_gpt(incoming_msg, number, assistant_manager)
        response = format_response(response)
        
        logging.info(f"Response generated for {sender_number}: {response}")
        
        # Send response
        resp = twilio_service.send_whatsapp(sender_number, response)
        logging.info(f"Response sent to {sender_number}")
        
        return str(resp)
        
    except Exception as e:
        logging.error(f"Error processing message for {sender_number}: {e}")
        # Send error message to user
        twilio_service = get_cached_twilio_service(db)
        error_response = "I'm sorry, something went wrong while processing your message. Please try again later."
        resp = twilio_service.send_whatsapp(sender_number, error_response)
        return str(resp)


@router.post(
    "/register-whatsapp-sender",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
)
async def register_whatsapp(
    sender_request: SenderRequest,
    twilio_service: TwilioService = Depends(get_twilio_service),
    current_user: User = Depends(get_current_user),
):
    """Register Whatsapp"""
    return twilio_service.register_whatsapp(sender_request, current_user)


@router.post(
    "/verify-sender/{sender_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
)
async def verification_sender(
    sender_id: str,
    verification_request: VerificationRequest,
    twilio_service: TwilioService = Depends(get_twilio_service),
    current_user: User = Depends(get_current_user),
):
    """Verify WhatsApp Sender"""
    return twilio_service.verify_sender(verification_request)


@router.get(
    "/sender/{sender_id}", status_code=status.HTTP_200_OK, response_class=JSONResponse
)
async def get_whatsapp_sender(
    sender_id: str,
    twilio_service: TwilioService = Depends(get_twilio_service),
    current_user: User = Depends(get_current_user),
):
    return twilio_service.get_whatsapp_sender(sender_id)


@router.post(
    "/update-sender", status_code=status.HTTP_200_OK, response_class=JSONResponse
)
async def update_whatsapp_sender(
    update_sender: UpdateSenderRequest,
    twilio_service: TwilioService = Depends(get_twilio_service),
    current_user: User = Depends(get_current_user),
):

    return twilio_service.update_whatsapp_sender(update_sender)


@router.delete("/sender", status_code=status.HTTP_200_OK, response_class=JSONResponse)
async def delete_whatsapp_sender(
    sender_id: SenderId,
    twilio_service: TwilioService = Depends(get_twilio_service),
    current_user: User = Depends(get_current_user),
):
    return twilio_service.delete_whatsapp_sender(sender_id)
