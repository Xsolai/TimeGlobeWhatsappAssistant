from ..core.config import settings
from twilio.rest import Client
from ..schemas.twilio_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
import requests
from fastapi import HTTPException, status


class TwilioService:
    def __init__(self):
        self.client = Client(settings.account_sid, settings.auth_token)

    def __get_header(self):
        return {"Content-Type": "application/json"}

    def __get_auth(self):
        """Return Twilio Auth account sid and auth token"""
        return (settings.account_sid, settings.auth_token)

    def send_whatsapp(self, to: str, message: str):
        print(f"account_id {settings.account_sid} auth_token {settings.auth_token}")
        # print(f"record==>> {to} and message is {message}")
        return self.client.messages.create(
            to=to,
            from_=f"whatsapp:{settings.from_whatsapp_number}",
            body=message,
        )

    def register_whatsapp(self, sender_request: SenderRequest):
        payload = {
            "sender_id": f"whatsapp:{sender_request.phone_number}",
            "waba_id": sender_request.waba_id,  # "whatsapp:+923197375742"
            "profile": {
                "name": sender_request.businees_name,
                "about": sender_request.about,
                "vertical": sender_request.business_type,
                "address": sender_request.address,
                "emails": [sender_request.email],
                "websites": [sender_request.website],
                "logo_url": sender_request.logo_url,
            },
            "webhook": {
                "callback_url": "https://30dc-2407-aa80-314-e0ca-1143-57c-3cbc-deec.ngrok-free.app/api/v1/webhook/whatsapp",
                "callback_method": "POST",
            },
        }
        response = requests.post(
            settings.TWILIO_API_URL,
            json=payload,
            headers=self.__get_header(),
            auth=self.__get_auth(),
        )
        print("status code==>> ", "Response===>>", response.json())
        if response.status_code == 201 or response.status_code == 200:
            return {
                "message": "Whatsapp registered Successfully",
                "data": response.json(),
            }
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json().get("message")
            )

    def verify_sender(self, verification_request: VerificationRequest):
        """Whatsapp Sender Verification"""
        payload = {
            "configuration": {
                "verification_code": verification_request.verification_code
            }
        }
        url = f"{settings.TWILIO_API_URL}/{verification_request.sender_id}"
        response = requests.post(
            url=url, auth=self.__get_auth(), headers=self.__get_header(), json=payload
        )
        print(
            "response ===>> ",
            f"status_code : {response.status_code} message :{response.json()}",
        )

        if response.status_code == 200:
            return {"message": "Verification Successfull", "data": response.json()}
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json().get("message")
            )

    def get_whatsapp_sender(self, sender_id: SenderId):
        """Fetch a Whatsapp Sender by providing sender id"""
        response = requests.get(
            url=f"{settings.TWILIO_API_URL}/{sender_id}",
            auth=self.__get_auth(),
            headers=self.__get_header(),
        )
        print("response ===>> ", response.json())
        if response.status_code == 200:
            return {"data": response.json()}
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json().get("message")
            )

    def update_whatsapp_sender(self, update_request: UpdateSenderRequest):
        """Update WhatsApp Sender"""
        payload = {
            "webhook": {
                "callback_method": "POST",
                "callback_url": "https://demo.twilio.com/new_webhook",
            },
            "profile": {"about": update_request.description},
        }
        response = requests.post(
            url=f"{settings.TWILIO_API_URL}/{update_request.sender_id}",
            auth=self.__get_auth(),
            headers=self.__get_header(),
            json=payload,
        )
        print(
            f"status_code==>> {response.status_code} \n response ===>> {response.json()}"
        )
        if response.status_code == 202:
            return {
                "message": "whatsapp sender updated Successfullly",
                "data": response.json(),
            }
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json().get("message")
            )

    def delete_whatsapp_sender(self, sender_id: SenderId):
        """Delete Whatsapp Sender"""

        response = requests.delete(
            url=f"{settings.TWILIO_API_URL}/{sender_id.sender_id}",
            auth=self.__get_auth(),
        )
        print("response ===>> ", response.json())
        if response.status_code == 200:
            return {"message": "Whatapp sender deleted Successfully"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("message"),
            )
