from pydantic import BaseModel, EmailStr

class OnboardingRequest(BaseModel):
    business_name: str
    email: EmailStr

class ConnectWhatsAppRequest(BaseModel):
    business_id: str
    phone_number: str
    friendly_name: str
