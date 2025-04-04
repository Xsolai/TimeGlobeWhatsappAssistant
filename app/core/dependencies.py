from ..services.twilio_service import TwilioService
from ..services.auth_service import AuthService, oauth2_scheme
from ..services.subscription_service import SubscriptionPlanService
from ..services.dashboard_service import DashboardService
from ..repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from fastapi import Depends, Request, HTTPException
from ..db.session import get_db
from .config import settings
from twilio.request_validator import RequestValidator

# from ..services.time_globe_service import TimeGlobeService


async def validate_twilio_request(request: Request):
    validator = RequestValidator(settings.auth_token)
    params = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")

    if not validator.validate(params=params, signature=signature, uri=str(request.url)):
        raise HTTPException(status_code=400, detail="Invalid Twilio request")


def get_twilio_service(db: Session = Depends(get_db)) -> TwilioService:
    return TwilioService(db)


def get_auth_service(db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    return AuthService(user_repository)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    return get_auth_service(db).get_current_user(token)


def get_subscription_service(db: Session = Depends(get_db)):
    return SubscriptionPlanService(db)


def get_dashboard_service(db: Session = Depends(get_db)):
    return DashboardService(db)


# def get_time_globe_service() -> TimeGlobeService:
#     return TimeGlobeService()
