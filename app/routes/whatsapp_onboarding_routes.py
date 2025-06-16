from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter()

@router.get("/onboarding-test", response_class=HTMLResponse)
async def get_onboarding_test_page():
    """Serve the WhatsApp onboarding test page."""
    with open("app/static/whatsapp_onboarding_test.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content) 