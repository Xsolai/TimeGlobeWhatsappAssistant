from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from .routes import auth_route, subscription_route, webhook_routes, analytics_routes, download_routes, contract_routes, auftragsverarbeitung_routes, lastschriftmandat_routes, whatsapp_status_routes, whatsapp_onboarding_routes
from .core.config import settings
from .db.session import engine, Base
from .utils.message_queue import MessageQueue
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth_route.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(subscription_route.router, prefix="/api/subscription", tags=["Subscription"])
app.include_router(webhook_routes.router, prefix="/api/whatsapp", tags=["Webhooks"])
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(download_routes.router, prefix="/api/download", tags=["Downloads"])
app.include_router(contract_routes.router, prefix="/api/contract", tags=["Contracts"])
app.include_router(auftragsverarbeitung_routes.router, prefix="/api/auftragsverarbeitung", tags=["Auftragsverarbeitung"])
app.include_router(lastschriftmandat_routes.router, prefix="/api/lastschriftmandat", tags=["Lastschriftmandat"])
app.include_router(whatsapp_status_routes.router, prefix="/api/whatsapp", tags=["WhatsApp Status"])
app.include_router(whatsapp_onboarding_routes.router, prefix="/api/whatsapp", tags=["WhatsApp Onboarding"])

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize message queue
message_queue = MessageQueue.get_instance()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Start message queue workers
        await message_queue.start_workers()
        logger.info("Message queue workers started")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        # Stop message queue workers
        await message_queue.stop_workers()
        logger.info("Message queue workers stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to TimeGlobe WhatsApp Assistant API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
