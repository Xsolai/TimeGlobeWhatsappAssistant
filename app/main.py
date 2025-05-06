from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .routes import auth_route, subscription_route, webhook_routes, analytics_routes, download_routes
from .core.config import settings
from .logger import main_logger
from .db.session import engine
from .models.base import Base
from .models.business_model import Business, WABAStatus
from .core.env import load_env
import logging
import requests
import json
import urllib.parse

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
    BusinessSubscription,
    SubscriptionPlan,
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

# Set up static files serving
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth_route.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(webhook_routes.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(subscription_route.router, prefix="/api/subscription", tags=["Subscription"])
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(download_routes.router, prefix="/api/download", tags=["Downloads"])


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

        # Handle client_created event
        if event_type == "client_created":
            # Extract client information from the payload
            client_info = data.get("client", {})
            client_id = client_info.get("id")
            client_name = client_info.get("name")
            contact_info = client_info.get("contact_info", {})
            client_email = contact_info.get("email")
            
            if client_email and client_name:
                try:
                    from sqlalchemy.orm import Session
                    from .utils.security_util import get_password_hash
                    import uuid
                    import string
                    import random
                    
                    # Generate a random temporary password
                    chars = string.ascii_letters + string.digits
                    temp_password = ''.join(random.choice(chars) for _ in range(12))
                    
                    with Session(engine) as db:
                        # Check if a business with this email already exists
                        existing_business = db.query(Business).filter(Business.email == client_email).first()
                        
                        if not existing_business:
                            # Create a new business record
                            new_business = Business(
                                id=str(uuid.uuid4()),
                                business_name=client_name,
                                email=client_email,
                                password=get_password_hash(temp_password),
                                client_id=client_id,
                                waba_status=WABAStatus.pending
                            )
                            
                            db.add(new_business)
                            db.commit()
                            logging.info(f"✅ Created new business record for client {client_name} with email {client_email}")
                            
                            # Here you could also send a welcome email with the temporary password
                            # and instructions to connect their WhatsApp account
                        else:
                            # Update existing business with client_id if not already set
                            if not existing_business.client_id:
                                existing_business.client_id = client_id
                                db.commit()
                                logging.info(f"✅ Updated existing business with client_id for {client_email}")
                            else:
                                logging.info(f"Business with email {client_email} already has client_id set")
                                
                except Exception as e:
                    logging.error(f"❌ Failed to create/update business record: {str(e)}")
            else:
                logging.error(f"Missing required client information. Email: {client_email}, Name: {client_name}")
            
            return {"status": "success"}

        elif event_type == "channel_permission_granted" and status == "ready":
            # Extract client information from the payload
            client_info = data.get("client", {})
            client_name = client_info.get("name")
            contact_info = client_info.get("contact_info", {})
            client_email = contact_info.get("email")
            
            # If client email not found in webhook data, try to fetch it from 360dialog API
            if not client_email and client_id:
                try:
                    # Make API call to get client info
                    url = f"https://hub.360dialog.io/api/v2/partners/{settings.PARTNER_ID}/clients"
                    headers = {
                        "Content-Type": "application/json",
                        "D360-API-KEY": settings.PARTNER_API_KEY
                    }
                    
                    logging.info(f"Fetching additional client info for client_id: {client_id}")
                    filters_json = json.dumps({"id": client_id})
                    encoded_filters = urllib.parse.quote(filters_json)
                    response = requests.get(f"{url}?filters={encoded_filters}", headers=headers)
                    
                    if response.status_code == 200:
                        api_client_data = response.json()
                        
                        if api_client_data.get("clients") and len(api_client_data["clients"]) > 0:
                            api_client_info = api_client_data["clients"][0]
                            api_contact_info = api_client_info.get("contact_info", {})
                            
                            # Update with API data if missing in webhook
                            client_email = client_email or api_contact_info.get("email")
                            client_name = client_name or api_client_info.get("name")
                except Exception as e:
                    logging.error(f"Error fetching additional client info: {str(e)}")
            
            # Extract setup info
            setup_info = data.get("setup_info", {})
            phone_number = setup_info.get("phone_number")
            
            # Ensure phone_number is correctly formatted (with or without + prefix)
            # Save without + prefix for consistency
            if phone_number and phone_number.startswith("+"):
                phone_number = phone_number[1:]
                
            phone_name = setup_info.get("phone_name")
            
            # Extract WABA account info
            waba_account = data.get("waba_account", {})
            
            # Prepare WhatsApp profile data
            whatsapp_profile = {
                "phone_number": phone_number,
                "phone_name": phone_name,
                "waba_id": waba_account.get("id"),
                "namespace": waba_account.get("namespace"),
                "fb_business_id": waba_account.get("fb_business_id"),
                "account_mode": data.get("account_mode"),
                "quality_rating": data.get("current_quality_rating"),
                "current_limit": data.get("current_limit")
            }
            
            # ✅ Channel is ready, now create an API key
            api_key_data = create_api_key(settings.PARTNER_ID or "MalHtRPA", channel_id)
            logging.info(f"🎯 API Key created for client {client_id}: {api_key_data}")

            # Save all information to the database
            if api_key_data:
                try:
                    from sqlalchemy.orm import Session
                    import bcrypt
                    
                    with Session(engine) as db:
                        # Check if a business with this email already exists
                        existing_business = None
                        if client_email:
                            existing_business = db.query(Business).filter(Business.email == client_email).first()
                        
                        if existing_business:
                            # Update existing business
                            existing_business.client_id = client_id
                            existing_business.channel_id = channel_id
                            existing_business.api_key = api_key_data["api_key"]
                            existing_business.api_endpoint = api_key_data["address"]
                            existing_business.app_id = api_key_data["app_id"]
                            existing_business.waba_status = WABAStatus.connected
                            existing_business.whatsapp_profile = whatsapp_profile
                            existing_business.business_name = client_name or existing_business.business_name
                            
                            # Store WhatsApp number in dedicated column (ensure it's without the + prefix)
                            if phone_number:
                                existing_business.whatsapp_number = phone_number
                                logging.info(f"Saved WhatsApp number: {phone_number} for business {existing_business.business_name}")
                            
                            db.commit()
                            logging.info(f"✅ Updated business information for {client_email}")
                        else:
                            # Log this case but don't create new business records at this stage
                            logging.info(f"No existing business found for email {client_email}. Skipping creation at this stage.")
                    
                except Exception as e:
                    logging.error(f"❌ Failed to save business information to database: {str(e)}")
        
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
        # Set webhook URL for this channel
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
    print(params)

    # Log or save the data as needed
    logging.info(f"✅ Received onboarding data: client_id={client_id}, channels={channels}, revoked={revoked}")

    # Fetch client information from 360dialog API
    if client_id:
        try:
            # Make API call to get client info
            url = f"https://hub.360dialog.io/api/v2/partners/{settings.PARTNER_ID}/clients"
            headers = {
                "Content-Type": "application/json",
                "D360-API-KEY": settings.PARTNER_API_KEY
            }
            
            logging.info(f"Fetching client info for client_id: {client_id}")
            # 360dialog API uses query parameters for filtering
            filters_json = json.dumps({"id": client_id})
            encoded_filters = urllib.parse.quote(filters_json)
            response = requests.get(f"{url}?filters={encoded_filters}", headers=headers)
            
            if response.status_code == 200:
                client_data = response.json()
                logging.info(f"Client data received: {client_data}")
                
                if client_data.get("clients") and len(client_data["clients"]) > 0:
                    client_info = client_data["clients"][0]
                    client_email = client_info.get("contact_info", {}).get("email")
                    client_name = client_info.get("name")
                    
                    if client_email:
                        # Try to find a business with this email
                        from sqlalchemy.orm import Session
                        from .models.business_model import Business, WABAStatus
                        
                        with Session(engine) as db:
                            business = db.query(Business).filter(Business.email == client_email).first()
                            
                            if business:
                                # Update business with client_id and channel_id
                                business.client_id = client_id
                                if channels:
                                    # Handle different formats of the channels parameter
                                    channel_ids = []
                                    if isinstance(channels, list):
                                        channel_ids = channels
                                    elif channels.startswith('[') and channels.endswith(']'):
                                        # Parse string format "[id]" to extract the ID
                                        try:
                                            channel_content = channels[1:-1].strip()
                                            if channel_content:
                                                channel_ids = [id.strip() for id in channel_content.split(',')]
                                        except Exception as e:
                                            logging.error(f"Error parsing channel string: {str(e)}")
                                    else:
                                        # Assume it's a single channel ID
                                        channel_ids = [channels]
                              
                                    if channel_ids:
                                        business.channel_id = channel_ids[0]  # Use the first channel ID
                                
                                business.business_name = client_name or business.business_name
                                business.waba_status = WABAStatus.connected
                                
                                # Fetch additional data if needed to populate whatsapp_number
                                if not business.whatsapp_number and channel_ids and len(channel_ids) > 0:
                                    try:
                                        channel_id = channel_ids[0]
                                        channel_url = f"https://hub.360dialog.io/api/v2/partners/{settings.PARTNER_ID}/channels/{channel_id}"
                                        channel_response = requests.get(channel_url, headers=headers)
                                        
                                        if channel_response.status_code == 200:
                                            channel_data = channel_response.json()
                                            setup_info = channel_data.get("setup_info", {})
                                            phone_number = setup_info.get("phone_number")
                                            
                                            # Format phone number consistently (without + prefix)
                                            if phone_number:
                                                if phone_number.startswith("+"):
                                                    phone_number = phone_number[1:]
                                                business.whatsapp_number = phone_number
                                                logging.info(f"Added WhatsApp number {phone_number} to business")
                                    except Exception as e:
                                        logging.error(f"Error fetching channel data: {str(e)}")
                                
                                db.commit()
                                logging.info(f"✅ Updated business record for email: {client_email} with client_id: {client_id}")
                            else:
                                logging.warning(f"❌ No matching business found for email: {client_email}")
                    else:
                        logging.warning("❌ No email found in client contact info")
                else:
                    logging.warning(f"❌ No client data found for client_id: {client_id}")
            else:
                logging.error(f"❌ Failed to fetch client info: {response.status_code} - {response.text}")
                
        except Exception as e:
            logging.error(f"❌ Error processing client data: {str(e)}")

    # Automatically close the tab without returning any content
    html_content = """
    <html>
        <head>
            <title>Closing...</title>
            <script>
                // Close the tab immediately
                window.close();
            </script>
        </head>
        <body>
            <p>Closing...</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/")
async def root():
    main_logger.info("Root endpoint accessed")
    return {"message": "Welcome to TimeGlobe WhatsApp Assistant API"}
