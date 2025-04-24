from ..core.config import settings
import requests
from ..repositories.dialog360_repository import Dialog360Repository
from ..schemas.dialog360_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
from ..schemas.auth import Business
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..logger import main_logger


class Dialog360Service:
    def __init__(self, db: Session):
        self.dialog360_repository = Dialog360Repository(db)
        self.logger = main_logger
        self.db = db

    @property
    def _header(self):
        return {
            "Content-Type": "application/json",
            "D360-API-KEY": settings.DIALOG360_API_KEY
        }

    def _make_request(
        self,
        method: str,
        payload: str,
        endpoint: str = None,
        success_message: str = None,
    ):
        """Make an HTTP request to the 360dialog API."""
        self.logger.info(
            f"Making {method} request to {endpoint} with payload: {payload}"
        )

        try:
            response = requests.request(
                method=method,
                url=endpoint,
                json=payload,
                headers=self._header,
            )

            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Request to {endpoint} successful: {response.json()}")
                return {"message": success_message, "data": response.json()}
            else:
                error_message = response.json().get("message", "Unknown error occurred")
                self.logger.error(f"Request to {endpoint} failed: {error_message}")
                raise HTTPException(
                    status_code=response.status_code, detail=error_message
                )
        except Exception as e:
            self.logger.exception(f"Exception during request to {endpoint}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    def send_whatsapp(self, to: str, message: str):
        """Send a WhatsApp message using 360dialog Cloud API"""
        self.logger.info(f"Sending WhatsApp message to {to}: {message}")
        
        # Format recipient number without "whatsapp:" prefix
        if to.startswith("whatsapp:"):
            to = to.replace("whatsapp:", "")
            
        # Make sure the number includes country code and starts with +
        if not to.startswith("+"):
            to = f"+{to}"
            
        try:
            # Construct payload using Cloud API format
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            # Use the Cloud API endpoint
            cloud_api_url = "https://waba-v2.360dialog.io/messages"
            
            response = self._make_request(
                "POST",
                payload,
                cloud_api_url,
                "Message sent successfully"
            )
            
            self.logger.info(f"WhatsApp message sent successfully via 360dialog")
            return response
        except Exception as e:
            self.logger.exception(f"Failed to send WhatsApp message: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to send WhatsApp message"
            )

    def register_whatsapp(self, sender_request: SenderRequest, business: Business):
        self.logger.info(f"Registering WhatsApp sender: {sender_request.phone_number}")

        payload = {
            "phone_number": sender_request.phone_number,
            "waba_id": sender_request.waba_id,
            "profile": {
                "name": sender_request.business_name,
                "about": sender_request.about,
                "address": sender_request.address,
                "email": sender_request.email,
                "vertical": sender_request.business_type,
                "photo": sender_request.logo_url,
                "description": sender_request.description,
                "websites": [sender_request.website],
            },
            "webhook_url": "http://18.184.65.167:3000/api/whatsapp/incoming-whatsapp",
        }

        response = self._make_request(
            "POST",
            payload,
            f"{settings.DIALOG360_API_URL}/channels",
            "WhatsApp Sender initiated successfully",
        )

        self.logger.info(f"WhatsApp sender registration response: {response}")
        return response

    def verify_sender(self, verification_request: VerificationRequest):
        """Whatsapp Sender Verification"""
        self.logger.info(
            f"Verifying WhatsApp sender ID: {verification_request.sender_id}"
        )

        payload = {
            "verification_code": verification_request.verification_code
        }
        
        url = f"{settings.DIALOG360_API_URL}/channels/{verification_request.sender_id}/verify"

        return self._make_request("POST", payload, url, "Verification successful")

    def get_whatsapp_sender(self, sender_id: str):
        """Fetch a WhatsApp Sender by providing sender ID"""
        self.logger.info(f"Fetching WhatsApp sender info for ID: {sender_id}")

        url = f"{settings.DIALOG360_API_URL}/channels/{sender_id}"
        self.dialog360_repository.get_sender(sender_id)

        return self._make_request(
            "GET", None, url, "WhatsApp Sender information retrieved"
        )

    def update_whatsapp_sender(self, update_request: UpdateSenderRequest):
        """Update WhatsApp Sender"""
        self.logger.info(f"Updating WhatsApp sender ID: {update_request.sender_id}")

        payload = {
            "profile": {
                "name": update_request.business_name,
                "about": update_request.about,
                "vertical": update_request.business_type,
                "address": update_request.address,
                "email": update_request.email,
                "websites": [update_request.website],
                "photo": update_request.logo_url,
                "description": update_request.description,
            },
            "webhook_url": "http://18.184.65.167:3000/api/whatsapp/incoming-whatsapp",
        }

        url = f"{settings.DIALOG360_API_URL}/channels/{update_request.sender_id}"

        return self._make_request(
            "PUT", payload, url, "WhatsApp sender updated successfully"
        )

    def delete_whatsapp_sender(self, sender_id: SenderId):
        """Delete WhatsApp Sender"""
        self.logger.info(f"Deleting WhatsApp sender ID: {sender_id.sender_id}")

        url = f"{settings.DIALOG360_API_URL}/channels/{sender_id.sender_id}"

        return self._make_request(
            "DELETE", None, url, "WhatsApp sender deleted successfully"
        ) 