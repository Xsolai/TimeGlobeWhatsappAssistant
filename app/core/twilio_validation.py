from .config import settings
from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException


async def validate_twilio_request(request: Request):
    validator = RequestValidator(settings.auth_token)
    params = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")

    if not validator.validate(params=params, signature=signature, uri=str(request.url)):
        raise HTTPException(status_code=400, detail="Invalid Twilio request")
