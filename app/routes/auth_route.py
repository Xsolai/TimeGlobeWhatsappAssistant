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


router = APIRouter()


@router.post("/register", response_class=JSONResponse)
def register(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.create_user(user_data)


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.create_token(user.email)


@router.post("/verify-otp", response_class=JSONResponse)
def verify_otp(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.verify_otp(request)


@router.post("/resend-otp", response_class=JSONResponse)
def resend_otp(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.resend_otp(request)


@router.post("/forget-password", response_class=JSONResponse)
def forget_password(
    request: OTPVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.forget_password(request)


@router.post("/reset-password", response_class=JSONResponse)
def reset_passowrd(
    request: ResetPasswordRequest, auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.reset_password(request)


@router.get("/users/me", response_model=User)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
