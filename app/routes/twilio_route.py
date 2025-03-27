from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
from functools import lru_cache
from twilio.twiml.messaging_response import MessagingResponse
import time

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

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Cache for AssistantManager instances
_assistant_manager_cache = {}
_cache_ttl = 300  # 5 minutes

def _get_assistant_manager(db: Session) -> AssistantManager:
    """Get or create an AssistantManager instance with caching."""
    cache_key = id(db)
    if cache_key in _assistant_manager_cache:
        manager, timestamp = _assistant_manager_cache[cache_key]
        if time.time() - timestamp < _cache_ttl:
            return manager
    
    manager = AssistantManager(settings.OPENAI_API_KEY, settings.OPENAI_ASSISTANT_ID, db)
    _assistant_manager_cache[cache_key] = (manager, time.time())
    return manager

@router.post("/incoming-whatsapp")
async def whatsapp_webhook(
    request: Request,
    twilio_service: TwilioService = Depends(get_twilio_service),
    db: Session = Depends(get_db),
):
    """
    Webhook to receive WhatsApp messages via Twilio.
    Responds with the processed message from get_response_from_gpt.
    """
    try:
        # Validate request first
        await validate_twilio_request(request)
        
        # Get form data
        form_data = await request.form()
        incoming_msg = form_data.get("Body", "").lower()
        sender_number = form_data.get("From", "")
        number = "".join(filter(str.isdigit, sender_number))
        
        if not incoming_msg or not sender_number:
            logger.warning("Missing required message data")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Missing required message data"}
            )

        logger.info(f"Processing message from {sender_number}: {incoming_msg}")
        
        # Get response using cached assistant manager
        assistant_manager = _get_assistant_manager(db)
        response = get_response_from_gpt(incoming_msg, number, assistant_manager)
        
        # Send response
        resp = twilio_service.send_whatsapp(sender_number, response)
        logger.info(f"Response sent to {sender_number}")
        
        return str(resp)
        
    except HTTPException as he:
        logger.error(f"HTTP error processing message: {str(he)}")
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail}
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"}
        )


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
