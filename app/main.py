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
import requests

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

        event_type = payload.get("event")
        data = payload.get("data", {})
        client_id = data.get("client_id")
        channel_id = data.get("id")
        status = data.get("status")

        if event_type == "channel_permission_granted" and status == "ready":
            # ✅ Channel is ready, now create an API key
            api_key = create_api_key(settings.PARTNER_ID or "MalHtRPA", channel_id)
            logging.info(f"🎯 API Key created for client {client_id}: {api_key}")

            # TODO: Save api_key securely in DB or wherever you want
        return {"status": "success"}
    
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    

    
def create_api_key(partner_id, channel_id):
    url = f"https://hub.360dialog.io/api/v2/partners/{partner_id}/channels/{channel_id}/api_keys"
    headers = {
        "Content-Type": "application/json",
        "D360-API-KEY": "794c76fd-7b5c-49a2-ae32-e123fabcac74"  
    }

    logging.info(f"Creating API key for partner {partner_id} and channel {channel_id}")
    logging.info(f"Headers: {headers}")
    logging.info(f"URL: {url}") 
    
    response = requests.post(url, headers=headers)
    if response.status_code == 201:
        result = response.json()
        api_data = {
            "address": result.get("address"),
            "api_key": result.get("api_key"),
            "app_id": result.get("app_id"),
            "id": result.get("id")
        }
        # set webhook url, for this channel now 
        # link https://waba-v2.360dialog.io/v1/configs/webhook
        #  body {
        #   "url": "https://solasolution.ecomtask.de/app3/api/whatsapp/incoming-whatsapp",
        #   "headers": {}
        # }
        # d360-api-key the api key we get in the result
        # Content-Type application/json
        # url is https://solasolution.ecomtask.de/app3/api/whatsapp/incoming-whatsapp
        
        
        #start code
        url = f"https://waba-v2.360dialog.io/v1/configs/webhook"
        headers = {
            "Content-Type": "application/json",
            "D360-API-KEY": api_data["api_key"]
        }   
        data = {
            "url": "https://solasolution.ecomtask.de/app3/api/whatsapp/incoming-whatsapp",
            "headers": {}
        }
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"Webhook set response: {response.json()}")    
        
        
        # Save to database
        try:
            from sqlalchemy.orm import Session
            from .models.onboarding_model import Business, WABAStatus
            
            with Session(engine) as db:
                # Find or create business record
                business = db.query(Business).filter(Business.client_id == partner_id).first()
                if not business:
                    business = Business(
                        client_id=partner_id,
                        channel_id=channel_id,
                        waba_status=WABAStatus.connected
                    )
                    db.add(business)
                
                # Update business with API information
                business.api_key = api_data["api_key"]
                business.api_endpoint = api_data["address"]
                business.app_id = api_data["app_id"]
                business.waba_status = WABAStatus.connected
                
                db.commit()
                
                logging.info(f"✅ Successfully saved API information for business with client_id {partner_id}")
        
        except Exception as e:
            logging.error(f"❌ Failed to save API information to database: {str(e)}")
            
        return api_data
    else:
        logging.error(f"❌ Failed to create API Key: {response.status_code} - {response.text}")
        return None

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
