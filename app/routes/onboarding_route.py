from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.onboarding import ConnectWhatsAppRequest
from app.services.twilio_service import TwilioService
from app.db.session import get_db
from app.models.onboarding_model import Business, WABAStatus
from app.core.dependencies import get_current_business
from sqlalchemy import text
import requests
from twilio.rest import Client

router = APIRouter(tags=["Onboarding"])

@router.post("/start")
def start_onboarding(
    db: Session = Depends(get_db),
    current_business: Business = Depends(get_current_business)
):
    # Check if business already has a Twilio account
    if current_business.twilio_subaccount_sid:
        raise HTTPException(
            status_code=400, 
            detail="Business already has a Twilio account"
        )

    service = TwilioService(db)
    twilio = service.create_twilio_subaccount(current_business.business_name)
    
    # # print raw twilio response
    # print(f"Raw Twilio response: {twilio}")
    
    # Validate the auth token
    if not twilio.get("auth_token") or str(twilio.get("auth_token"))=='None':
        raise HTTPException(
            status_code=500, 
            detail="Twilio did not return an auth token"
        )
    
    # Debug logging to verify auth token
    # print(f"Subaccount created with SID: {twilio['sid']} and auth token: {twilio['auth_token']}")
    
    # Set only the SID on the model, not the auth token
    current_business.twilio_subaccount_sid = twilio["sid"]
    current_business.waba_status = WABAStatus.pending
    
    # Commit the model changes
    db.commit()
    db.refresh(current_business)
    
    # Use direct SQL to set the auth token
    try:
        # Direct SQL update to bypass any model validation or event listeners
        token_result = db.execute(
            text("UPDATE businesses SET twilio_auth_token = :token WHERE id = :id"),
            {"token": twilio["auth_token"], "id": current_business.id}
        )
        db.commit()
        # print(f"Direct SQL auth token update: {token_result.rowcount} rows affected")
    except Exception as e:
        print(f"Direct SQL auth token update failed: {str(e)}")
        
    # Refresh to see if auth token was saved
    db.refresh(current_business)
    
    # Verify values after commit
    # print(f"After direct SQL update, SID: {current_business.twilio_subaccount_sid} and auth token: {current_business.twilio_auth_token}")

    return {"message": "Business onboarded", "business_id": str(current_business.id)}

@router.post("/connect-whatsapp")
def connect_whatsapp(
    data: ConnectWhatsAppRequest, 
    db: Session = Depends(get_db),
    current_business: Business = Depends(get_current_business)
):
    if not current_business.twilio_subaccount_sid or not current_business.twilio_auth_token:
        raise HTTPException(
            status_code=400, 
            detail="Business must complete onboarding first"
        )

    service = TwilioService(db)
    
    # Create a client for the business's subaccount
    business_client = Client(current_business.twilio_subaccount_sid, current_business.twilio_auth_token)
    
    try:
        # Initialize variables to track what was created vs reused
        resources_status = {
            "phone_number": "existing" if current_business.whatsapp_number else "new",
            "messaging_service": "existing" if current_business.messaging_service_sid else "new",
            "whatsapp_sender": "existing" if current_business.whatsapp_sender_sid else "new"
        }
        
        # Check if business already has a WhatsApp sender
        if (current_business.whatsapp_number and 
            current_business.whatsapp_sender_sid and 
            current_business.waba_id == data.waba_id):
            # print(f"Business already has complete WhatsApp configuration with WABA ID: {current_business.waba_id}")
            
            return {
                "message": "Business already has a complete WhatsApp configuration",
                "phone_number": current_business.whatsapp_number,
                "messaging_service_sid": current_business.messaging_service_sid,
                "whatsapp_sender_sid": current_business.whatsapp_sender_sid,
                "waba_id": current_business.waba_id,
                "status": current_business.waba_status,
                "resources_status": resources_status
            }
        
        # Step 1: Get or purchase a phone number
        phone_number = None
        number_info = None
        
        if current_business.whatsapp_number:
            # print(f"Using existing phone number: {current_business.whatsapp_number}")
            phone_number = current_business.whatsapp_number
            if current_business.phone_number_sid:
                # print(f"Phone number already has SID: {current_business.phone_number_sid}")
                number_info = {
                    "sid": current_business.phone_number_sid,
                    "phone_number": current_business.whatsapp_number,
                    "status": "existing"
                }
            else:
                # Get info for the existing number
                # print(f"Getting details for existing phone number: {current_business.whatsapp_number}")
                number_info = service.purchase_phone_number(
                    business_client=business_client,
                    existing_number=current_business.whatsapp_number
                )
                # Update phone_number_sid if it wasn't set
                if number_info and number_info.get("sid"):
                    current_business.phone_number_sid = number_info["sid"]
        else:
            # Purchase a new phone number
            # print(f"Purchasing phone number for business {current_business.business_name} in country {data.country_code}")
            number_info = service.purchase_phone_number(
                business_client=business_client,
                country_code=data.country_code
            )
            phone_number = number_info['phone_number']
            # print(f"Successfully purchased phone number: {phone_number}")
            current_business.whatsapp_number = phone_number
            if number_info.get("sid"):
                current_business.phone_number_sid = number_info["sid"]
        
        # Step 2: Get or create a messaging service
        messaging_service = None
        if current_business.messaging_service_sid:
            # print(f"Using existing messaging service: {current_business.messaging_service_sid}")
            # Get the existing messaging service
            try:
                messaging_service = business_client.messaging.v1.services(current_business.messaging_service_sid).fetch()
                # print(f"Found existing messaging service: {messaging_service.friendly_name}")
            except Exception as e:
                # print(f"Could not retrieve existing messaging service: {str(e)}")
                # Create a new one if we can't fetch the existing one
                messaging_service = service._get_or_create_messaging_service(
                    f"{current_business.business_name} WhatsApp Service", 
                    client=business_client
                )
                current_business.messaging_service_sid = messaging_service.sid
        else:
            # print(f"Creating messaging service for number {phone_number}")
            messaging_service = service._get_or_create_messaging_service(
                f"{current_business.business_name} WhatsApp Service", 
                client=business_client
            )
            # print(f"Created messaging service with SID: {messaging_service.sid}")
            current_business.messaging_service_sid = messaging_service.sid
        
        # Step 3: Check if WhatsApp sender exists or create a new one
        sender_info = None
        if current_business.whatsapp_sender_sid and current_business.waba_id == data.waba_id:
            # print(f"Using existing WhatsApp sender: {current_business.whatsapp_sender_sid}")
            # Just return what we have
            sender_info = {
                "status": current_business.whatsapp_status or "active",
                "sender_id": current_business.whatsapp_sender_id,
                "sid": current_business.whatsapp_sender_sid,
                "waba_id": current_business.waba_id,
                "profile": current_business.whatsapp_profile or {}
            }
        else:
            # If WABA ID is different or there's no sender, create a new one
            if current_business.waba_id != data.waba_id:
                print(f"WABA ID has changed from {current_business.waba_id} to {data.waba_id}")
            
            # Get the phone number without +
            formatted_phone = phone_number
            if formatted_phone.startswith("+"):
                formatted_phone = formatted_phone[1:]
                
            # print(f"Creating/updating WhatsApp sender for number {phone_number}")
            sender_info = service.create_whatsapp_sender(
                phone_number=formatted_phone,
                waba_id=data.waba_id,
                business=current_business
            )
            
            # print(f"Created/updated WhatsApp sender with SID: {sender_info['sid']}")
        
        # Update business record with WhatsApp sender information
        if not current_business.whatsapp_number:
            current_business.whatsapp_number = phone_number
            
        current_business.waba_status = WABAStatus.connected
        current_business.waba_id = data.waba_id
        
        if sender_info:
            current_business.whatsapp_sender_sid = sender_info["sid"]
            current_business.whatsapp_sender_id = sender_info["sender_id"]
            current_business.whatsapp_status = sender_info["status"]
            
            if sender_info.get("profile"):
                current_business.whatsapp_profile = {
                    "name": sender_info["profile"].get("name", ""),
                    "about": sender_info["profile"].get("about", ""),
                    "vertical": sender_info["profile"].get("vertical", ""),
                    "description": sender_info["profile"].get("description", "")
                }
        
        # Update resources_status based on what was actually done
        resources_status = {
            "phone_number": "existing" if current_business.whatsapp_number == phone_number else "new",
            "messaging_service": "existing" if current_business.messaging_service_sid == messaging_service.sid else "new",
            "whatsapp_sender": "existing" if (current_business.whatsapp_sender_sid and 
                                             current_business.whatsapp_sender_sid == sender_info["sid"]) else "new"
        }
        
        db.commit()
        db.refresh(current_business)
        
        return {
            "message": "WhatsApp configuration complete",
            "phone_number": current_business.whatsapp_number,
            "messaging_service_sid": current_business.messaging_service_sid,
            "whatsapp_sender_sid": current_business.whatsapp_sender_sid,
            "waba_id": current_business.waba_id,
            "resources_status": resources_status,
            "sender_info": sender_info
        }
    except Exception as e:
        # print(f"Error connecting WhatsApp: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect WhatsApp: {str(e)}"
        )

@router.get("/status")
def get_status(
    db: Session = Depends(get_db),
    current_business: Business = Depends(get_current_business)
):
    return {
        "business_name": current_business.business_name,
        "waba_status": current_business.waba_status,
        "twilio_subaccount_sid": current_business.twilio_subaccount_sid,
        "whatsapp_number": current_business.whatsapp_number,
        "messaging_service_sid": current_business.messaging_service_sid
    }

@router.post("/update-auth-token/{business_id}")
def update_auth_token(
    business_id: str,
    auth_token: str,
    db: Session = Depends(get_db)
):
    # Direct SQL update to bypass any model validations or triggers
    try:
        result = db.execute(
            text("UPDATE businesses SET twilio_auth_token = :token WHERE id = :id"),
            {"token": auth_token, "id": business_id}
        )
        db.commit()
        # print(f"Auth token update result: {result.rowcount} rows affected")
        return {"message": "Auth token updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update auth token: {str(e)}"
        )
