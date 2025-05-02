import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.auth import (
    Token,
    BusinessCreate,
    Business,
    OTPVerificationRequest,
    ResetPasswordRequest,
)
from ..services.auth_service import AuthService
from ..core.dependencies import get_auth_service, get_current_business

from ..logger import main_logger  # Ensure you have a logging setup

router = APIRouter()


@router.post("/register", response_class=JSONResponse)
def register(
    business_data: BusinessCreate, auth_service: AuthService = Depends(get_auth_service)
):
    """Handles business registration."""
    main_logger.info(f"Registering new business: {business_data.email}")
    try:
        result = auth_service.create_business(business_data)
        main_logger.info(f"Business registered successfully: {business_data.email}")
        return result
    except Exception as e:
        main_logger.error(f"Registration failed for {business_data.email}: {e}")
        raise HTTPException(status_code=400, detail="Registration failed")


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Handles business login and token generation."""
    main_logger.info(f"Login attempt for {form_data.username}")
    business = auth_service.authenticate_business(form_data.username, form_data.password)
    if not business:
        main_logger.warning(f"Failed login attempt for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_service.create_token(business.email)
    main_logger.info(f"Business {form_data.username} logged in successfully")
    return token


@router.post("/verify-otp", response_class=JSONResponse)
def verify_otp(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verifies the OTP for a business."""
    main_logger.info(f"Verifying OTP for {request.email}")
    return auth_service.verify_otp(request)


@router.post("/resend-otp", response_class=JSONResponse)
def resend_otp(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Resends OTP to the business's email."""
    main_logger.info(f"Resending OTP for {request.email}")
    return auth_service.resend_otp(request)


@router.post("/forget-password", response_class=JSONResponse)
def forget_password(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Handles forgot password flow and sends OTP for password reset."""
    main_logger.info(f"Password reset requested for {request.email}")
    return auth_service.forget_password(request)


@router.post("/reset-password", response_class=JSONResponse)
def reset_password(
    request: ResetPasswordRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Resets business password after OTP verification."""
    main_logger.info(f"Resetting password with token")
    return auth_service.reset_password(request)


@router.get("/business/me", response_model=Business)
def get_business_profile(current_business: Business = Depends(get_current_business)):
    """Fetches the logged-in business's profile."""
    main_logger.info(f"Fetching profile for {current_business.email}")
    return current_business
