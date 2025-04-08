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
from ..logger import main_logger

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

otp_storage = {}
# Temporary in-memory storage for reset tokens
reset_tokens: Dict[str, int] = {}


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        main_logger.debug(f"Attempting to authenticate user with email: {email}")
        user = self.user_repository.get_by_email(email)
        if not user:
            main_logger.warning(f"User with email {email} not found")
            return None
        if not verify_password(password, user.password):
            main_logger.warning(f"Invalid password for user with email: {email}")
            return None
        main_logger.info(f"User authenticated successfully: {email}")
        return user

    def create_user(self, user_data: UserCreate) -> dict:
        main_logger.debug(f"Creating user with email: {user_data.email}")
        # Check if email exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            main_logger.warning(f"Email already registered: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        expiry = time.time() + 300  # OTP valid for 5 minutes
        
        # check if the timeglobe auth key is valid and it returns a customerCd from the timeglobe api
        # if not valid, raise an exception
        # if valid, store the customerCd in the user_data object
        # Send request to API using the following endpoint /bot/getConfig using POST method and self.request method
        # Headers
        headers = {
            "x-book-auth-key": user_data.time_globe_auth_key,
            "Content-Type": "application/json;charset=UTF-8",
        }
        response = self.request(
                "GET",
                "/bot/getConfig",
                headers=headers,
            )
        if response.status_code != 200:
            main_logger.warning(f"Invalid timeglobe auth key: {user_data.time_globe_auth_key}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timeglobe auth key",
            )
            
        customer_cd = response.json().get("customerCd")
        otp = self.generate_otp()
        otp_storage[user_data.email] = {
            "otp": otp,
            "expiry": expiry,
            "data": {
                "name": user_data.name,
                "email": user_data.email,
                "password": user_data.password,
                "customerCd": customer_cd,
                "time_globe_auth_key": user_data.time_globe_auth_key,
            },
        }
        main_logger.debug(f"OTP generated for {user_data.email}: {otp}")
        body = f"Dear User,\n\nYour OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you!"

        email_util.send_email(user_data.email, "OTP Verification", body)
        main_logger.info(f"OTP sent to {user_data.email}")

        return {
            "message": "OTP sent to your email. Please verify to complete registration."
        }

    def create_token(self, user_email: str) -> Token:
        main_logger.debug(f"Creating token for user: {user_email}")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
        access_token = create_access_token(
            subject=user_email, expire_time=access_token_expires
        )
        main_logger.info(f"Token created for user: {user_email}")
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserModel:
        main_logger.debug("Fetching current user from token")
        payload = decode_token(token)
        user_email: str = payload.get("sub")
        user = self.user_repository.get_by_email(user_email)
        if user is None:
            main_logger.warning(f"User not found for token: {token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        main_logger.info(f"Current user fetched: {user_email}")
        return user

    def generate_otp(self, length=6):
        otp = "".join(secrets.choice(string.digits) for _ in range(length))
        main_logger.debug(f"Generated OTP: {otp}")
        return otp

    def verify_otp(self, request: OTPVerificationRequest):
        main_logger.debug(f"Verifying OTP for email: {request.email}")
        stored_otp = otp_storage.get(request.email)
        if not stored_otp:
            main_logger.warning(f"No OTP found for email: {request.email}")
            raise HTTPException(status_code=400, detail="No OTP found for this email.")
        if time.time() > stored_otp["expiry"]:
            otp_storage.pop(request.email, None)
            main_logger.warning(f"OTP expired for email: {request.email}")
            raise HTTPException(status_code=400, detail="OTP expired!")
        if stored_otp["otp"] != request.otp:
            main_logger.warning(f"Invalid OTP for email: {request.email}")
            raise HTTPException(status_code=400, detail="Invalid OTP")
        user_data = stored_otp["data"]
        _user = UserCreate(**user_data)
        self.user_repository.create(_user)
        otp_storage.pop(request.email)
        main_logger.info(f"User registered successfully: {request.email}")
        return {"message": "Registration Successful"}

    def resend_otp(self, request: OTPVerificationRequest):
        main_logger.debug(f"Resending OTP for email: {request.email}")
        stored_otp_data = otp_storage.get(request.email)
        if not stored_otp_data:
            main_logger.warning(
                f"No registration process found for email: {request.email}"
            )
            raise HTTPException(
                status_code=404, detail="No registration process found for this email."
            )

        otp = self.generate_otp()
        expiry = time.time() + 300  # New OTP valid for 5 minutes

        otp_storage[request.email]["otp"] = otp
        otp_storage[request.email]["expiry"] = expiry
        body = f"Dear User,\n\nYour OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you!"

        email_util.send_email(request.email, "Registration OTP", body)
        main_logger.info(f"OTP resent to {request.email}")
        return {
            "message": "OTP has been resent to your email. Please verify to complete registration."
        }

    def forget_password(self, request: OTPVerificationRequest):
        main_logger.debug(
            f"Processing forgot password request for email: {request.email}"
        )
        user = self.user_repository.get_by_email(request.email)
        if not user:
            main_logger.warning(f"User not found for email: {request.email}")
            raise HTTPException(
                status_code=404, detail="User with this email does not exist"
            )

        reset_token = str(uuid4())
        reset_tokens[reset_token] = user.id

        reset_link = f"https://frontend.d1qj820rqysre7.amplifyapp.com/reset-password/{user.id}/{reset_token}"
        # reset_link = f"insert-link"
        subject = "Reset Your Password"
        body = f"Hello {user.name},\n\nClick the link below to reset your password:\n{reset_link}\n\nBest regards,\nYour App Team"

        email_util.send_email(user.email, subject, body)
        main_logger.info(f"Reset password link sent to {request.email}")
        return {"message": "Reset password link has been sent to your email."}

    def reset_password(self, data: ResetPasswordRequest):
        main_logger.debug("Processing reset password request")
        if data.token not in reset_tokens:
            main_logger.warning(f"Invalid or expired reset token: {data.token}")
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )

        user_id = reset_tokens[data.token]
        user = self.user_repository.get_by_id(user_id)

        if not user:
            main_logger.warning(f"User not found for reset token: {data.token}")
            raise HTTPException(status_code=404, detail="User not found")

        self.user_repository.update(user.id, data.new_password)
        reset_tokens.pop(data.token, None)
        main_logger.info(f"Password reset successfully for user: {user.email}")
        return {
            "message": "Password reset successfully. You can now log in with your new password."
        }
