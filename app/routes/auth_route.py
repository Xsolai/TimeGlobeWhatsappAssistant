import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.auth import (
    Token,
    UserCreate,
    User,
    OTPVerificationRequest,
    ResetPasswordRequest,
)
from ..services.auth_service import AuthService
from ..core.dependencies import get_auth_service, get_current_user

from ..logger import main_logger  # Ensure you have a logging setup

router = APIRouter()


@router.post("/register", response_class=JSONResponse)
def register(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    """Handles user registration."""
    main_logger.info(f"Registering new user: {user_data.email}")
    try:
        result = auth_service.create_user(user_data)
        main_logger.info(f"User registered successfully: {user_data.email}")
        return result
    except Exception as e:
        main_logger.error(f"Registration failed for {user_data.email}: {e}")
        raise HTTPException(status_code=400, detail="Registration failed")


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Handles user login and token generation."""
    main_logger.info(f"Login attempt for {form_data.username}")
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        main_logger.warning(f"Failed login attempt for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_service.create_token(user.email)
    main_logger.info(f"User {form_data.username} logged in successfully")
    return token


@router.post("/verify-otp", response_class=JSONResponse)
def verify_otp(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verifies the OTP for a user."""
    main_logger.info(f"Verifying OTP for {request.email}")
    return auth_service.verify_otp(request)


@router.post("/resend-otp", response_class=JSONResponse)
def resend_otp(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Resends OTP to the user's email."""
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
    """Resets user password after OTP verification."""
    main_logger.info(f"Resetting password for {request.email}")
    return auth_service.reset_password(request)


@router.get("/users/me", response_model=User)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Fetches the logged-in user's profile."""
    main_logger.info(f"Fetching profile for {current_user.email}")
    return current_user






