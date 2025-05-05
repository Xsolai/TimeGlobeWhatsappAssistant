import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from ..schemas.auth import (
    Token,
    BusinessCreate,
    Business,
    OTPVerificationRequest,
    ResetPasswordRequest,
    TimeGlobeAuthKeyRequest,
    TimeGlobeAuthKeyResponse,
    BusinessInfoUpdate,
    BusinessInfoDelete,
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


@router.post("/validate-timeglobe-key", response_model=TimeGlobeAuthKeyResponse)
def validate_timeglobe_key(
    request: TimeGlobeAuthKeyRequest,
    current_business: Business = Depends(get_current_business),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Validates TimeGlobe API key and updates the business record if valid."""
    main_logger.info(f"Validating TimeGlobe API key for {current_business.email}")
    
    # If no auth_key provided, check if business already has valid credentials
    if not request.auth_key:
        if current_business.customer_cd and current_business.timeglobe_auth_key:
            return {
                "valid": True,
                "customer_cd": current_business.customer_cd,
                "message": "TimeGlobe authentication key already validated"
            }
        return {
            "valid": False,
            "message": "No TimeGlobe authentication key provided"
        }
    
    # Normal validation with auth_key
    result = auth_service.validate_timeglobe_auth_key(request.auth_key, current_business.email)
    return result


@router.get("/business/timeglobe-key", response_model=dict)
def get_timeglobe_auth_key(current_business: Business = Depends(get_current_business)):
    """Get the TimeGlobe auth key and customer_cd for the logged-in business."""
    return {
        "timeglobe_auth_key": current_business.timeglobe_auth_key,
        "customer_cd": current_business.customer_cd
    }


# Add a new schema that includes email for public validation
class PublicTimeGlobeAuthKeyRequest(BaseModel):
    auth_key: Optional[str] = None
    email: EmailStr


@router.post("/public/validate-timeglobe-key", response_model=TimeGlobeAuthKeyResponse)
def validate_timeglobe_key_public(
    request: PublicTimeGlobeAuthKeyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Validates TimeGlobe API key without requiring authentication."""
    main_logger.info(f"Validating TimeGlobe API key publicly for {request.email}")
    
    # If no auth_key provided, check if business already has valid credentials
    if not request.auth_key:
        # Check if business exists and has TimeGlobe credentials
        business = auth_service.business_repository.get_by_email(request.email)
        if business and business.customer_cd and business.timeglobe_auth_key:
            return {
                "valid": True,
                "customer_cd": business.customer_cd,
                "message": "TimeGlobe authentication key already validated"
            }
        return {
            "valid": False,
            "message": "No TimeGlobe authentication key provided"
        }
    
    # Normal validation with auth_key
    result = auth_service.validate_timeglobe_auth_key(request.auth_key, request.email)
    return result


@router.post("/update-business-info", response_model=dict)
def update_business_info(
    business_info_update: BusinessInfoUpdate,
    current_business: Business = Depends(get_current_business),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Updates business information."""
    main_logger.info(f"Updating business information for {current_business.email}")
    try:
        result = auth_service.update_business_info(current_business, business_info_update)
        main_logger.info(f"Business information updated successfully for {current_business.email}")
        return result
    except Exception as e:
        main_logger.error(f"Failed to update business information for {current_business.email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-business-info", response_model=dict)
def delete_business_info(
    fields: BusinessInfoDelete,
    current_business: Business = Depends(get_current_business),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Deletes specific business information fields."""
    main_logger.info(f"Deleting business information fields for {current_business.email}: {fields.fields}")
    try:
        result = auth_service.delete_business_info_fields(current_business, fields.fields)
        main_logger.info(f"Business information fields deleted successfully for {current_business.email}")
        return result
    except Exception as e:
        main_logger.error(f"Failed to delete business information fields: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business/info", response_model=Business)
def get_business_info(current_business: Business = Depends(get_current_business)):
    """Gets the complete business information."""
    main_logger.info(f"Fetching business information for {current_business.email}")
    return current_business
