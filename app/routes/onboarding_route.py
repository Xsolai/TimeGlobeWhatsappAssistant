from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.onboarding import OnboardingRequest, ConnectWhatsAppRequest
from app.services.twilio_service import TwilioService
from app.db.session import get_db
from app.models.onboarding_model import Business, WABAStatus

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.post("/start")
def start_onboarding(data: OnboardingRequest, db: Session = Depends(get_db)):
    service = TwilioService(db)
    twilio = service.create_twilio_subaccount(data.business_name)

    business = Business(
        name=data.business_name,
        email=data.email,
        twilio_subaccount_sid=twilio["sid"],
        twilio_auth_token=twilio["auth_token"],
        waba_status=WABAStatus.pending
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    return {"message": "Business onboarded", "business_id": str(business.id)}

@router.post("/connect-whatsapp")
def connect_whatsapp(data: ConnectWhatsAppRequest, db: Session = Depends(get_db)):
    service = TwilioService(db)
    business = db.query(Business).filter(Business.id == data.business_id).first()

    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    sender_sid = service.create_whatsapp_sender(
        sub_sid=business.twilio_subaccount_sid,
        sub_auth_token=business.twilio_auth_token,
        phone_number=data.phone_number,
        friendly_name=data.friendly_name
    )

    business.whatsapp_number = data.phone_number
    business.waba_status = WABAStatus.connected
    db.commit()

    return {"message": "WhatsApp sender connected", "sender_sid": sender_sid}

@router.get("/status/{business_id}")
def get_status(business_id: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()

    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    return {
        "business_name": business.name,
        "waba_status": business.waba_status,
        "twilio_subaccount_sid": business.twilio_subaccount_sid,
        "whatsapp_number": business.whatsapp_number
    }
