from datetime import timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..repositories.user_repository import UserRepository
from ..utils.security_util import verify_password, create_access_token, decode_token
from ..schemas.auth import (
    Token,
    UserCreate,
    OTPVerificationRequest,
    ResetPasswordRequest,
    User,
)
from ..models.user import UserModel
from ..core.config import settings
from ..utils import email_util
import secrets, string, time
from uuid import uuid4

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

otp_storage = {}
# Temporary in-memory storage for reset tokens
reset_tokens: Dict[str, int] = {}


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def create_user(self, user_data: UserCreate) -> dict:
        # Check if email exists
        if self.user_repository.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        expiry = time.time() + 300  # OTP valid for 5 minutes
        otp = self.generate_otp()
        otp_storage[user_data.email] = {
            "otp": otp,
            "expiry": expiry,
            "data": {
                "name": user_data.name,
                "email": user_data.email,
                "password": user_data.password,
            },
        }
        print(otp_storage)
        body = f"Dear User,\n\nYour OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you!"

        email_util.send_email(user_data.email, "OTP Verification", body)

        return {
            "message": "OTP sent to your email. Please verify to complete registration."
        }

    def create_token(self, user_email: str) -> Token:
        # access_token_expires = timedelta(minutes=30)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
        access_token = create_access_token(
            subject=user_email, expire_time=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserModel:
        payload = decode_token(token)
        user_email: str = payload.get("sub")
        user = self.user_repository.get_by_email(user_email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def generate_otp(self, length=6):
        # Using only digits for OTP
        return "".join(secrets.choice(string.digits) for _ in range(length))

    def verify_otp(self, request: OTPVerificationRequest):
        stored_otp = otp_storage.get(request.email)
        if not stored_otp:
            raise HTTPException(status_code=400, detail="No OTP found for this email.")
        if time.time() > stored_otp["expiry"]:
            otp_storage.pop(request.email, None)
            raise HTTPException(status_code=400, detail="OTP expired!")
        if stored_otp["otp"] != request.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        user_data = stored_otp["data"]
        _user = UserCreate(**user_data)
        self.user_repository.create(_user)
        otp_storage.pop(request.email)
        return {"message": "Registration Successfull"}

    def resend_otp(self, request: OTPVerificationRequest):
        stored_otp_data = otp_storage.get(request.email)
        if not stored_otp_data:
            raise HTTPException(
                status_code=404, detail="No registration process found for this email."
            )

        # Generate a new OTP
        otp = self.generate_otp()
        expiry = time.time() + 300  # New OTP valid for 5 minutes

        # Update OTP storage
        otp_storage[request.email]["otp"] = otp
        otp_storage[request.email]["expiry"] = expiry
        body = f"Dear User,\n\nYour OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you!"

        email_util.send_email(request.email, "Registration OTP", body)
        return {
            "message": "OTP has been resent to your email. Please verify to complete registration."
        }

    def forget_password(self, request: OTPVerificationRequest):
        user = self.user_repository.get_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email does not exist",
            )

        # Generate a unique reset token
        reset_token = str(uuid4())
        reset_tokens[reset_token] = user.id  # Map token to user ID

        # Construct reset link with uid/token format
        reset_link = f"https://frontend.d1qj820rqysre7.amplifyapp.com/reset-password/{user.id}/{reset_token}"

        # Send the reset password email
        subject = "Reset Your Password"
        body = (
            f"Hello {user.name},\n\n"
            "We received a request to reset your password. Click the link below to reset it:\n"
            f"{reset_link}\n\n"
            "If you did not request this, please ignore this email.\n\n"
            "Best regards,\nYour App Team"
        )
        email_util.send_email(user.email, subject, body)

        return {"message": "Reset password link has been sent to your email."}

    def reset_password(self, data: ResetPasswordRequest):
        if data.token not in reset_tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Get the user ID associated with the token
        user_id = reset_tokens[data.token]  # Do not pop the token here
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # Check if the new password matches the last password
        if verify_password(data.new_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as the last password",
            )
        arg = {"password": data.new_password}
        self.user_repository.update(user.id, data.new_password)

        # Remove the token only after successful reset
        reset_tokens.pop(data.token, None)

        return {
            "message": "Password reset successfully. You can now log in with your new password."
        }
