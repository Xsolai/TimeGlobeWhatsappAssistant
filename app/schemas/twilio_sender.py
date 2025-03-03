from pydantic import BaseModel
from typing import Optional


class SenderRequest(BaseModel):
    phone_number: str
    businees_name: str
    about: str
    business_type: str
    address: str
    email: str
    website: str
    logo_url: str
    waba_id: str
    # callback_url: str


class SenderId(BaseModel):
    sender_id: str


class VerificationRequest(BaseModel):
    verification_code: str


class UpdateSenderRequest(SenderId):
    description: str
