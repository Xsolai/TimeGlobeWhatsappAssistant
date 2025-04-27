from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .routes import auth_route, onboarding_route, twilio_route, subscription_route, twilio_webhook_route
from .core.config import settings
from .logger import main_logger
from .db.session import engine
from .models.base import Base
from .core.env import load_env
import logging

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables at startup
main_logger.info("Loading environment variables...")
env = load_env()
main_logger.info("Environment variables loaded")

# Import all models to ensure they are registered with SQLAlchemy
from .models.all_models import (
    Business, 
    WABAStatus,
    BusinessSubscription,
    SubscriptionPlan,
    WASenderModel,
    ThreadModel,
    ActiveRunModel,
    BookingDetail,
    BookModel,
    CustomerModel
)
# Import database setup function
from .db.setup_db import setup_database
import os

app = FastAPI(
    title="TimeGlobe WhatsApp Assistant API",
    version="1.0.0",
    description="TimeGlobe WhatsApp Assistant API powered by 360dialog",
)

# Initialize database and ensure all tables are created
setup_database()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_route.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(onboarding_route.router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(twilio_route.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(subscription_route.router, prefix="/api/subscription", tags=["Subscription"])
app.include_router(twilio_webhook_route.router, prefix="/api/twilio", tags=["Twilio Webhooks"])



@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        payload = await request.json()
        logging.info(f"Received webhook: {payload}")
       
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

@app.get("/redirect", response_class=HTMLResponse)
async def handle_redirect(request: Request):
    # Get query parameters
    params = dict(request.query_params)
    client_id = params.get("client")
    channels = params.get("channels")
    revoked = params.get("revoked")

    # Log or save the data as needed
    print(f"✅ Received onboarding data: client_id={client_id}, channels={channels}, revoked={revoked}")

    # Here you can save this info in DB or memory (optional)

    # Show a success message to the user
    html_content = f"""
    <html>
        <head>
            <title>Onboarding Completed</title>
        </head>
        <body style="font-family:Arial;text-align:center;margin-top:50px;">
            <h1>🎉 Onboarding Completed!</h1>
            <p><strong>Client ID:</strong> {client_id}</p>
            <p><strong>Channels:</strong> {channels}</p>
            <p>Now you can close this page and start using WhatsApp API!</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/")
async def root():
    main_logger.info("Root endpoint accessed")
    return {"message": "Welcome to TimeGlobe WhatsApp Assistant API"}
