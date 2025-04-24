from ..services.dialog360_service import Dialog360Service
from ..services.auth_service import AuthService, oauth2_scheme
from ..services.subscription_service import SubscriptionPlanService
from sqlalchemy.orm import Session
from fastapi import Depends, Request, HTTPException
from ..db.session import get_db
from .config import settings
from fastapi.security import OAuth2PasswordBearer
from typing import Generator
from ..db.session import SessionLocal
from ..repositories.business_repository import BusinessRepository
from ..models.onboarding_model import Business


def get_dialog360_service(db: Session = Depends(get_db)) -> Dialog360Service:
    return Dialog360Service(db)


def get_business_repository(db: Session = Depends(get_db)) -> BusinessRepository:
    return BusinessRepository(db)


def get_auth_service(business_repository: BusinessRepository = Depends(get_business_repository)) -> AuthService:
    return AuthService(business_repository)


async def get_current_business(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Business:
    auth_service = AuthService(db)
    business = await auth_service.get_current_business(token)
    return business


def get_subscription_service(db: Session = Depends(get_db)):
    return SubscriptionPlanService(db)


# def get_time_globe_service() -> TimeGlobeService:
#     return TimeGlobeService()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
