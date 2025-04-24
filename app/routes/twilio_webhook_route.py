from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from twilio.request_validator import RequestValidator
from app.core.config import settings

router = APIRouter(tags=["Twilio Webhooks"])

def validate_twilio_request(request: Request):
    """Validate that the request is coming from Twilio"""
    validator = RequestValidator(settings.auth_token)
    url = str(request.url)
    params = dict(request.query_params)
    signature = request.headers.get("X-Twilio-Signature", "")
    
    if not validator.validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

@router.post("/status-callback")
async def handle_status_callback(request: Request, db: Session = Depends(get_db)):
    """Handle message status callbacks from Twilio"""
    # Validate Twilio request
    validate_twilio_request(request)
    
    # Parse the status update
    form_data = await request.form()
    message_sid = form_data.get("MessageSid", "")
    message_status = form_data.get("MessageStatus", "")
    
    # Log the status update
    # print(f"Message {message_sid} status: {message_status}")
    
    return {"status": "success"} 