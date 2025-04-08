from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    time_globe_auth_key = Field(..., min_length=8)
    customer_cd = Field(...)


class UserInDB(UserCreate):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class OTPVerificationRequest(BaseModel):
    email: str
    otp: str = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
