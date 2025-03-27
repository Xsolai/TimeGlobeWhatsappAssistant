from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time
from collections import defaultdict
from typing import Dict, Tuple
import threading

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
from ..utils.tools_wrapper_util import get_response_from_gpt
from ..utils.tools_wrapper_util import format_response
import logging
from twilio.twiml.messaging_response import MessagingResponse
from ..db.session import get_db
from ..core.dependencies import (
    get_twilio_service,
    validate_twilio_request,
    get_current_user,
)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_REQUESTS_PER_WINDOW = 30  # Maximum requests per minute per user
rate_limit_data: Dict[str, list] = defaultdict(list)
rate_limit_lock = threading.RLock()

def check_rate_limit(user_id: str) -> bool:
    """Check if the user has exceeded the rate limit."""
    current_time = time.time()
    
    with rate_limit_lock:
        # Clean up old timestamps
        rate_limit_data[user_id] = [ts for ts in rate_limit_data[user_id] 
                                  if current_time - ts < RATE_LIMIT_WINDOW]
        
        # Check if user has exceeded rate limit
        if len(rate_limit_data[user_id]) >= MAX_REQUESTS_PER_WINDOW:
            return False
            
        # Add current timestamp
        rate_limit_data[user_id].append(current_time)
        return True

router = APIRouter()


@router.post("/incoming-whatsapp")
async def whatsapp_wbhook(
    request: Request,
    tiwilio_service: TwilioService = Depends(get_twilio_service),
    db: Session = Depends(get_db),
):
    """
    Webhook to receive WhatsApp messages via Twilio.
    Responds with the processed message from get_response_from_gpt.
    """
    form_data = await request.form()
    await validate_twilio_request(request)

    incoming_msg = form_data.get("Body", "").lower()  # The incoming message body
    sender_number = form_data.get("From", "")  # Sender's WhatsApp number
    number = "".join(filter(str.isdigit, sender_number))
    
    # Check rate limit
    if not check_rate_limit(number):
        logging.warning(f"Rate limit exceeded for user {number}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": "Rate limit exceeded. Please try again later."}
        )
    
    logging.info(f"Incoming message from {sender_number}: {incoming_msg}")
    try:
        # Get response from the assistant function
        _assistant_manager = AssistantManager(
            settings.OPENAI_API_KEY, settings.OPENAI_ASSISTANT_ID, db
        )
        response = get_response_from_gpt(incoming_msg, number, _assistant_manager)
        response = format_response(response)

        logging.info(f"Response generated for {sender_number}: {response}")
    except Exception as e:
        logging.error(f"Error generating response for {sender_number}: {e}")
        response = "I'm sorry, something went wrong while processing your message."
    
    print(f"Response ==>> {sender_number} with: {response}")
    resp = tiwilio_service.send_whatsapp(sender_number, response)
    print("Resp", str(resp))
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
