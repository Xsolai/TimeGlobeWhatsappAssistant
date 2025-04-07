from ..core.config import settings
from twilio.rest import Client
from ..repositories.twilio_repository import TwilioRepository
from ..repositories.user_repository import UserRepository
from ..schemas.twilio_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
from ..schemas.auth import User
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..logger import main_logger


class TwilioService:
    def __init__(self, db: Session):
        self.twilio_repository = TwilioRepository(db)
        self.user_repository = UserRepository(db)
        self.message_service_id = settings.TWILIO_MESSAGING_SERVICE_SID
        self.client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

    @property
    def _header(self):
        return {"Content-Type": "application/json"}

    @property
    def _auth(self):
        """Return Twilio Auth account sid and auth token"""
        return (settings.ACCOUNT_SID, settings.AUTH_TOKEN)

    def _make_request(
        self,
        method: str,
        payload: str,
        endpoint: str = None,
        success_message: str = None,
    ):
        """Make an HTTP request to the Twilio API."""
        main_logger.info(
            f"Making {method} request to {endpoint} with payload: {payload}"
        )

        try:
            response = requests.request(
                method=method,
                url=endpoint,
                json=payload,
                headers=self._header,
                auth=self._auth,
            )

            if response.status_code in [200, 201, 202]:
                main_logger.info(f"Request to {endpoint} successful: {response.json()}")
                return {"message": success_message, "data": response.json()}
            else:
                error_message = response.json().get("message", "Unknown error occurred")
                main_logger.error(f"Request to {endpoint} failed: {error_message}")
                raise HTTPException(
                    status_code=response.status_code, detail=error_message
                )
        except Exception as e:
            main_logger.exception(f"Exception during request to {endpoint}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    def send_whatsapp(self, to: str, message: str):
        main_logger.info(f"Sending WhatsApp message to {to}: {message}")
        try:
            response = self.client.messages.create(
                messaging_service_sid=self.message_service_id,
                to=to,
                from_=settings.FROM_WHATSAPP_NUMBER,
                body=message,
            )
            main_logger.info(f"WhatsApp message sent successfully: {response.sid}")
            return response
        except Exception as e:
            main_logger.exception(f"Failed to send WhatsApp message: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to send WhatsApp message"
            )

    def register_whatsapp(self, sender_request: SenderRequest, user: User):
        main_logger.info(f"Registering WhatsApp sender: {sender_request.phone_number}")
        payload = {
            "sender_id": f"whatsapp:{sender_request.phone_number}",
            "waba_id": sender_request.waba_id,
            "profile": {
                "name": sender_request.business_name,
                "about": sender_request.about,
                "address": sender_request.address,
                "emails": [sender_request.email],
                "vertical": sender_request.business_type,
                "logo_url": sender_request.logo_url,
                "description": sender_request.description,
                "websites": sender_request.website,
            },
            "webhook": {
                "callback_url": "http://18.184.65.167:3000/api/twilio/incoming-whatsapp",
                "callback_method": "POST",
            },
        }

        response = self._make_request(
            "POST",
            payload,
            settings.TWILIO_API_URL,
            "WhatsApp Sender initiated successfully",
        )

        main_logger.info(f"WhatsApp sender registration response: {response}")
        if response.get("status"):
            self.twilio_repository.create_whatsapp_sender(
                sender_data=sender_request,
                sender_id=sender_request.phone_number,
                status=response.get("status"),
                user=user
            )
        return response

    def verify_sender(self, verification_request: VerificationRequest):
        """Whatsapp Sender Verification"""
        main_logger.info(
            f"Verifying WhatsApp sender ID: {verification_request.sender_id}"
        )

        payload = {
            "configuration": {
                "verification_code": verification_request.verification_code
            }
        }
        url = f"{settings.TWILIO_API_URL}/{verification_request.sender_id}"

        return self._make_request("POST", payload, url, "Verification successful")

    def get_whatsapp_sender(self, sender_id: SenderId):
        """Fetch a WhatsApp Sender by providing sender ID"""
        main_logger.info(f"Fetching WhatsApp sender info for ID: {sender_id}")

        url = f"{settings.TWILIO_API_URL}/{sender_id}"
        self.twilio_repository.get_sender(sender_id)

        return self._make_request(
            "GET", None, url, "WhatsApp Sender information retrieved"
        )

    def update_whatsapp_sender(self, update_request: UpdateSenderRequest):
        """Update WhatsApp Sender"""
        main_logger.info(f"Updating WhatsApp sender ID: {update_request.sender_id}")

        payload = {
            "webhook": {
                "callback_method": "POST",
                "callback_url": "https://demo.twilio.com/new_webhook",
            },
            "profile": {
                "name": update_request.business_name,
                "about": update_request.about,
                "vertical": update_request.business_type,
                "address": update_request.address,
                "emails": [update_request.email],
                "websites": [update_request.website],
                "logo_url": update_request.logo_url,
                "description": update_request.description,
            },
        }

        url = f"{settings.TWILIO_API_URL}/{update_request.sender_id}"

        return self._make_request(
            "POST", payload, url, "WhatsApp sender updated successfully"
        )

    def delete_whatsapp_sender(self, sender_id: SenderId):
        """Delete WhatsApp Sender"""
        main_logger.info(f"Deleting WhatsApp sender ID: {sender_id.sender_id}")

        url = f"{settings.TWILIO_API_URL}/{sender_id.sender_id}"

        return self._make_request(
            "DELETE", None, url, "WhatsApp sender deleted successfully"
        )
