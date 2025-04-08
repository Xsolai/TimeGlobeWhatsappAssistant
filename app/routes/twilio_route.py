from fastapi import APIRouter, Request, Depends, HTTPException, status

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
import json
from datetime import datetime,timezone
from twilio.twiml.messaging_response import MessagingResponse
from ..db.session import get_db
from ..core.dependencies import (
    get_twilio_service,
    validate_twilio_request,
    get_current_user,
)
from ..models.customer_model import CustomerModel
from ..models.booked_appointment import BookModel
from ..models.booking_detail import BookingDetail
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone,timedelta
from ..logger import main_logger
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter()

def get_assistant_manager(db: Session = Depends(get_db)) -> AssistantManager:
    return AssistantManager(
        settings.OPENAI_API_KEY,
        settings.OPENAI_ASSISTANT_ID,
        db
    )

def get_current_time_info():
    tz = timezone(timedelta(hours=2))  # GMT+2
    now = datetime.now(tz)
    return datetime.today().date(), now.strftime('%H:%M:%S')

@router.post("/incoming-whatsapp")
async def whatsapp_webhook(
    request: Request,
    twilio_service: TwilioService = Depends(get_twilio_service),
    assistant_manager: AssistantManager = Depends(get_assistant_manager)
):
    """
    Webhook to receive WhatsApp messages via Twilio and respond using GPT assistant.
    """
    try:
        form_data = await request.form()
        await validate_twilio_request(request)

        incoming_msg = form_data.get("Body", "").strip().lower()
        sender = form_data.get("From", "")
        receiver = form_data.get("To", "")
        number = "".join(filter(str.isdigit, sender))

        main_logger.info(f"Incoming message from {sender} to {receiver}: {incoming_msg}")

        date_str, time_str = get_current_time_info()
        enriched_msg = f"{incoming_msg}\nCurrent date: {date_str}\nCurrent time: {time_str}"

        raw_response = get_response_from_gpt(enriched_msg, number, assistant_manager, receiver)
        formatted_response = format_response(raw_response)

        # Structured log
        main_logger.info(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": sender,
            "receiver": receiver,
            "message": incoming_msg,
            "response": formatted_response,
        }))

        twilio_service.send_whatsapp(sender, formatted_response)

        main_logger.info(
            f"Responded to customer {sender} for question '{incoming_msg}' with response '{formatted_response}'"
        )

        return formatted_response

    except Exception as e:
        main_logger.error(f"Error in processing message from {form_data.get('From', '')}: {str(e)}")
        return "I'm sorry, something went wrong while processing your message."


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
