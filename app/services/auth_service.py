from datetime import timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..repositories.business_repository import BusinessRepository
from ..utils.security_util import verify_password, create_access_token, decode_token
from ..schemas.auth import (
    Token,
    BusinessCreate,
    OTPVerificationRequest,
    ResetPasswordRequest,
    Business,
)
from ..models.business_model import Business
from ..core.config import settings
from ..utils import email_util
from ..services.timeglobe_service import TimeGlobeService
import secrets, string, time
from uuid import uuid4
from ..logger import main_logger

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

otp_storage = {}
# Temporary in-memory storage for reset tokens
reset_tokens: Dict[str, int] = {}


class AuthService:
    def __init__(self, business_repository: BusinessRepository):
        self.business_repository = business_repository

    def authenticate_business(self, email: str, password: str) -> Optional[Business]:
        main_logger.debug(f"Attempting to authenticate business with email: {email}")
        business = self.business_repository.get_by_email(email)
        if not business:
            main_logger.warning(f"Business with email {email} not found")
            return None
        if not verify_password(password, business.password):
            main_logger.warning(f"Invalid password for business with email: {email}")
            return None
        main_logger.info(f"Business authenticated successfully: {email}")
        return business

    def create_business(self, business_data: BusinessCreate) -> dict:
        main_logger.debug(f"Creating business with email: {business_data.email}")
        # Check if email exists
        existing_business = self.business_repository.get_by_email(business_data.email)
        if existing_business:
            main_logger.warning(f"Email already registered: {business_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
            
        # Validate TimeGlobe auth key if provided
        customer_cd = None
        if business_data.timeglobe_auth_key:
            timeglobe_service = TimeGlobeService()
            validation_result = timeglobe_service.validate_auth_key(business_data.timeglobe_auth_key)
            
            if not validation_result.get("valid", False):
                main_logger.warning(f"Invalid TimeGlobe auth key for {business_data.email}: {validation_result.get('message')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation_result.get('message', "Invalid TimeGlobe authentication key")
                )
                
            customer_cd = validation_result.get("customer_cd")
            main_logger.info(f"Valid TimeGlobe auth key with customerCd: {customer_cd} for {business_data.email}")
        else:
            return {
                "message": "TimeGlobe auth key is required"
            }

        expiry = time.time() + 300  # OTP valid for 5 minutes
        otp = self.generate_otp()
        otp_storage[business_data.email] = {
            "otp": otp,
            "expiry": expiry,
            "data": {
                "business_name": business_data.business_name,
                "email": business_data.email,
                "password": business_data.password,
                "phone_number": business_data.phone_number,
                "timeglobe_auth_key": business_data.timeglobe_auth_key,
                "customer_cd": customer_cd
            },
        }

        main_logger.debug(f"OTP generated for {business_data.email}: {otp}")
        body = f"Dear Business Owner,\n\nYour OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you!"

        email_util.send_email(business_data.email, "OTP Verification", body)
        main_logger.info(f"OTP sent to {business_data.email}")

        return {
            "message": "OTP sent to your email. Please verify to complete registration."
        }

    def create_token(self, business_email: str) -> Token:
        main_logger.debug(f"Creating token for business: {business_email}")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
        access_token = create_access_token(
            subject=business_email, expire_time=access_token_expires
        )
        main_logger.info(f"Token created for business: {business_email}")
        return Token(access_token=access_token, token_type="bearer")

    def get_current_business(self, token: str = Depends(oauth2_scheme)) -> Business:
        main_logger.debug("Fetching current business from token")
        payload = decode_token(token)
        business_email: str = payload.get("sub")
        business = self.business_repository.get_by_email(business_email)
        if business is None:
            main_logger.warning(f"Business not found for token: {token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Business not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        main_logger.info(f"Current business fetched: {business_email}")
        return business

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
            
        business_data = stored_otp["data"]
        
        # Create business using repository
        new_business = self.business_repository.create_business(
            business_name=business_data["business_name"],
            email=business_data["email"],
            password=business_data["password"],
            phone_number=business_data["phone_number"],
            timeglobe_auth_key=business_data.get("timeglobe_auth_key"),
            customer_cd=business_data.get("customer_cd")
        )

        otp_storage.pop(request.email)
        main_logger.info(f"Business registered successfully: {request.email}")
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
        body = f"Dear Business Owner,\n\nYour OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you!"

        email_util.send_email(request.email, "Registration OTP", body)
        main_logger.info(f"OTP resent to {request.email}")
        return {
            "message": "OTP has been resent to your email. Please verify to complete registration."
        }

    def forget_password(self, request: OTPVerificationRequest):
        main_logger.debug(
            f"Processing forgot password request for email: {request.email}"
        )
        business = self.business_repository.get_by_email(request.email)
        if not business:
            main_logger.warning(f"Business not found for email: {request.email}")
            raise HTTPException(
                status_code=404, detail="Business with this email does not exist"
            )

        reset_token = str(uuid4())
        reset_tokens[reset_token] = business.id

        reset_link = f"https://frontend.d1qj820rqysre7.amplifyapp.com/reset-password/{business.id}/{reset_token}"

        subject = "Reset Your Password"
        body = f"Hello {business.business_name},\n\nClick the link below to reset your password:\n{reset_link}\n\nBest regards,\nYour App Team"

        email_util.send_email(business.email, subject, body)
        main_logger.info(f"Reset password link {reset_link} sent to {request.email}")
        return {"message": "Reset password link has been sent to your email."}

    def reset_password(self, data: ResetPasswordRequest):
        main_logger.debug("Processing reset password request")
        if data.token not in reset_tokens:
            main_logger.warning(f"Invalid or expired reset token: {data.token}")
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )

        business_id = reset_tokens[data.token]
        business = self.business_repository.get_by_id(business_id)
        if not business:
            main_logger.warning(f"Business not found for ID: {business_id}")
            raise HTTPException(status_code=404, detail="Business not found")

        self.business_repository.update_password(business_id, data.new_password)
        reset_tokens.pop(data.token)
        main_logger.info(f"Password reset for business: {business.email}")
        return {"message": "Password has been reset successfully"}
