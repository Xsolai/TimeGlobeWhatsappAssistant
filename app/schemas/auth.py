from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class BusinessBase(BaseModel):
    business_name: str
    email: EmailStr
    phone_number: Optional[str] = None


class BusinessCreate(BusinessBase):
    password: str
    timeglobe_auth_key: Optional[str] = None


class Business(BusinessBase):
    id: str
    is_active: bool
    created_at: datetime
    whatsapp_number: Optional[str] = None
    customer_cd: Optional[str] = None  # TimeGlobe customer code
    timeglobe_auth_key: Optional[str] = None

    class Config:
        from_attributes = True


class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class TokenPayload(BaseModel):
    sub: str
    exp: int
