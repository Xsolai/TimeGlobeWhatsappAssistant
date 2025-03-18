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


class TwilioService:
    def __init__(self, db: Session):
        self.twilio_repository = TwilioRepository(db)
        self.user_repository = UserRepository(db)
        self.message_service_id = settings.TWILIO_MESSAGING_SERVICE_SID
        self.client = Client(settings.account_sid, settings.auth_token)

    @property
    def _header(self):
        return {"Content-Type": "application/json"}

    @property
    def _auth(self):
        """Return Twilio Auth account sid and auth token"""
        return (settings.account_sid, settings.auth_token)

    def _make_request(
        self,
        method: str,
        payload: str,
        endpoint: str = None,
        success_message: str = None,
    ):
        """Make an HTTP request to the Twilio API."""
        try:
            if payload:
                response = requests.request(
                    method=method,
                    url=endpoint,
                    json=payload,
                    headers=self._header,
                    auth=self._auth,
                )
            else:
                response = requests.request(
                    method=method,
                    url=endpoint,
                    headers=self._header,
                    auth=self._auth,
                )
            if response.status_code in [200, 201, 202]:
                return {"message": success_message, "data": response.json()}
            else:
                error_message = response.json().get("message", "Unknown error occurred")
                raise HTTPException(
                    status_code=response.status_code, detail=error_message
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    def send_whatsapp(self, to: str, message: str):
        print(f"send+++ {to} ,{settings.from_whatsapp_number}, {message}")
        return self.client.messages.create(
            messaging_service_sid=self.message_service_id,
            to=to,
            from_=settings.from_whatsapp_number,
            body=message,
        )

    def register_whatsapp(self, sender_request: SenderRequest, user: User):
        payload = {
            "sender_id": f"whatsapp:{sender_request.phone_number}",
            "waba_id": sender_request.waba_id,
            "profile": {
                "name": sender_request.business_name,
                "about": sender_request.about,
                "vertical": sender_request.business_type,
                "address": sender_request.address,
                "emails": [sender_request.email],
                "websites": [sender_request.website],
                "logo_url": sender_request.logo_url,
                "description": sender_request.description,
            },
            "webhook": {
                "callback_url": "https://4674-103-167-159-226.ngrok-free.app/api/twilio/incoming-whatsapp",
                "callback_method": "POST",
            },
        }
        response = self._make_request(
            "POST",
            payload,
            settings.TWILIO_API_URL,
            "WhatsApp Sender initiated Successfully",
        )
        print(f"response==>>{response}")
        if response:
            sid = response.get("data", {}).get("sid", None)
            self.twilio_repository.create_whatsapp_sender(sender_request, sid, user)

        return response

    def verify_sender(self, verification_request: VerificationRequest):
        """Whatsapp Sender Verification"""
        payload = {
            "configuration": {
                "verification_code": verification_request.verification_code
            }
        }
        url = f"{settings.TWILIO_API_URL}/{verification_request.sender_id}"
        return self._make_request("POST", payload, url, "Verification Successfull")

    def get_whatsapp_sender(self, sender_id: SenderId):
        """Fetch a Whatsapp Sender by providing sender id"""
        url = f"{settings.TWILIO_API_URL}/{sender_id}"
        self.twilio_repository.get_sender(sender_id)
        return self._make_request(
            "GET",
            payload=None,
            endpoint=url,
            success_message="WhatApp Sender Information",
        )

    def update_whatsapp_sender(self, update_request: UpdateSenderRequest):
        """Update WhatsApp Sender"""
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
        # self.twilio_repository.update_sender(update_request.sender_id, update_request)
        return self._make_request(
            "POST", payload, url, "whatsapp sender updated Successfullly"
        )

    def delete_whatsapp_sender(self, sender_id: SenderId):
        """Delete Whatsapp Sender"""
        url = f"{settings.TWILIO_API_URL}/{sender_id.sender_id}"
        return self._make_request(
            "DELETE",
            endpoint=url,
            payload=None,
            success_message="WhatsApp Sender Deleted Successfully",
        )
