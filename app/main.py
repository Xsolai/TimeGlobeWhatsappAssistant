from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth_route, onboarding_route, twilio_route, subscription_route, twilio_webhook_route
from .core.config import settings
from .logger import main_logger
from .db.session import engine
from .models.base import Base
from dotenv import load_dotenv
import os

# Always load .env at startup
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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

@app.get("/")
async def root():
    main_logger.info("Root endpoint accessed")
    return {"message": "Welcome to TimeGlobe WhatsApp Assistant API"}
