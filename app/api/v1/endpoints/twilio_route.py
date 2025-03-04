from fastapi import APIRouter, Request, Depends, HTTPException, status
from ....core.twilio_validation import validate_twilio_request
from ....services.twilio_service import TwilioService
from ....schemas.twilio_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
from ....assistant import get_response_from_gpt
from ....utils.tools_wrapper_util import format_response
import logging
from twilio.twiml.messaging_response import MessagingResponse


router = APIRouter()


@router.post("/incoming-whatsapp")
async def whatsapp_wbhook(request: Request):
    """
    Webhook to receive WhatsApp messages via Twilio.
    Responds with the processed message from get_response_from_gpt.
    """
    form_data = await request.form()
    print("res==>>", form_data)
    # await validate_twilio_request(request)

    incoming_msg = form_data.get("Body", "").lower()  # The incoming message body
    sender_number = form_data.get("From", "")  # Sender's WhatsApp number
    number = "".join(filter(str.isdigit, sender_number))
    logging.info(f"Incoming message from {sender_number}: {incoming_msg}")
    try:
        # Get response from the assistant function
        response = get_response_from_gpt(incoming_msg, sender_number)
        response = format_response(response)

        logging.info(f"Response generated for {sender_number}: {response}")
    except Exception as e:
        logging.error(f"Error generating response for {sender_number}: {e}")
        response = "I'm sorry, something went wrong while processing your message."
    # # Send the response back to the incoming message
    print(f"Response ==>> {sender_number} with: {response}")

    resp = MessagingResponse()
    resp.message(response)
    logging.info(f"Responded to {sender_number} with: {response}")
    print("Resp", str(resp))
    return str(resp)  # Respond to Twilio's webhook with the message


@router.post("/register-whatsapp-sender", status_code=status.HTTP_200_OK)
async def register_whatsapp(
    sender_request: SenderRequest,
    twilio_service: TwilioService = Depends(TwilioService),
):
    """Register Whatsapp"""
    return twilio_service.register_whatsapp(sender_request)


@router.post("/verify-sender/{sender_id}", status_code=status.HTTP_200_OK)
async def verification_sender(
    sender_id: str,
    verification_request: VerificationRequest,
    twilio_service: TwilioService = Depends(TwilioService),
):
    """Verify WhatsApp Sender"""
    return twilio_service.verify_sender(verification_request)


@router.get("/sender/{sender_id}", status_code=status.HTTP_200_OK)
async def get_whatsapp_sender(
    sender_id: str, twilio_service: TwilioService = Depends(TwilioService)
):
    return twilio_service.get_whatsapp_sender(sender_id)


@router.post("/update-sender", status_code=status.HTTP_200_OK)
async def update_whatsapp_sender(
    update_sender: UpdateSenderRequest,
    twilio_service: TwilioService = Depends(TwilioService),
):

    return twilio_service.update_whatsapp_sender(update_sender)


@router.delete("/sender", status_code=status.HTTP_200_OK)
async def delete_whatsapp_sender(
    sender_id: SenderId, twilio_service: TwilioService = Depends(TwilioService)
):
    return twilio_service.delete_whatsapp_sender(sender_id)
