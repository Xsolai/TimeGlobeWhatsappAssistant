from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
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

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# Initialize database and ensure all tables are created
setup_database()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routers import whatsapp, auth, appointments

app.include_router(whatsapp.router, prefix="/api/v1", tags=["whatsapp"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(appointments.router, prefix="/api/v1", tags=["appointments"])

@app.get("/")
async def root():
    main_logger.info("Root endpoint accessed")
    return {"message": "Welcome to TimeGlobe WhatsApp Assistant API"}
