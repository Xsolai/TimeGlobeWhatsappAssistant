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
from ..logger import main_logger

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
    receiver_nunmber = form_data.get("To", "")
    number = "".join(filter(str.isdigit, sender_number))
    main_logger.info(
        f"Incoming message from {sender_number} to {receiver_nunmber}: {incoming_msg}"
    )
    try:
        # Get response from the assistant function
        _assistant_manager = AssistantManager(
            settings.OPENAI_API_KEY, settings.OPENAI_ASSISTANT_ID, db
        )
        response = get_response_from_gpt(incoming_msg, number, _assistant_manager,receiver_nunmber.split(":")[1])
        response = format_response(response)
        main_logger.info(json.dumps(
                {
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "sender": sender_number,
                    "receiver": receiver_nunmber,
                    "message": incoming_msg,
                    "response": response,  
                }
            ))
        main_logger.info(f"Response generated for {sender_number}: {response}")
    except Exception as e:
        main_logger.error(f"Error generating response for {sender_number}: {e}")
        response = "I'm sorry, something went wrong while processing your message."
    # # Send the response back to the incoming message
    # print(f"Response ==>> {sender_number} with: {response}")

    # resp = MessagingResponse()
    # resp.message(response)
    resp = tiwilio_service.send_whatsapp(sender_number, response)
    main_logger.info(
        f"Responded to  customer {sender_number} for question {incoming_msg} with response {response}"
    )
    # print("Resp", str(resp))
    return str(resp)  # Respond to Twilio's webhook with the message


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
