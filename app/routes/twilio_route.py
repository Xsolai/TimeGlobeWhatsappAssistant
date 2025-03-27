from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from cachetools import TTLCache
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
import logging
from twilio.twiml.messaging_response import MessagingResponse
from ..db.session import get_db
from ..core.dependencies import (
    get_twilio_service,
    validate_twilio_request,
    get_current_user,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = FastAPILimiter()

# Initialize thread cache with 1 hour TTL
thread_cache = TTLCache(maxsize=1000, ttl=3600)

router = APIRouter()

@router.on_event("startup")
async def startup():
    await limiter.init()

@router.post("/incoming-whatsapp")
@limiter.limit("30/minute")  # Rate limit of 30 requests per minute per IP
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
        # Validate request and extract data
        form_data = await request.form()
        await validate_twilio_request(request)

        incoming_msg = form_data.get("Body", "").lower()
        sender_number = form_data.get("From", "")
        number = "".join(filter(str.isdigit, sender_number))
        
        logger.info(f"Incoming message from {sender_number}: {incoming_msg}")

        # Check cache for existing thread
        thread_id = thread_cache.get(number)
        
        # Initialize assistant manager with cached thread if available
        _assistant_manager = AssistantManager(
            settings.OPENAI_API_KEY, 
            settings.OPENAI_ASSISTANT_ID, 
            db,
            thread_id=thread_id  # Pass thread_id if available
        )

        # Process message and get response
        response = await _assistant_manager.process_message(number, incoming_msg)
        response = format_response(response)

        # Update cache with new thread ID if created
        if not thread_id and _assistant_manager.current_thread_id:
            thread_cache[number] = _assistant_manager.current_thread_id

        logger.info(f"Response generated for {sender_number}: {response}")
        
        # Send response
        resp = twilio_service.send_whatsapp(sender_number, response)
        logger.info(f"Response sent to {sender_number}")
        
        return str(resp)

    except Exception as e:
        logger.error(f"Error processing message from {sender_number}: {e}")
        error_response = "I'm sorry, something went wrong while processing your message."
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
