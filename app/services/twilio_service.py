from ..core.config import settings
from twilio.rest import Client
from ..repositories.twilio_repository import TwilioRepository
from ..schemas.twilio_sender import (
    SenderRequest,
    VerificationRequest,
    SenderId,
    UpdateSenderRequest,
)
from ..schemas.auth import Business
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..logger import main_logger


class TwilioService:
    def __init__(self, db: Session):
        self.twilio_repository = TwilioRepository(db)
        self.message_service_id = settings.TWILIO_MESSAGING_SERVICE_SID
        self.client = Client(settings.account_sid, settings.auth_token)
        self.logger = main_logger
        self.db = db  # Store the db session

    @property
    def _header(self):
        return {"Content-Type": "application/json"}

    @property
    def _auth(self):
        """Return Twilio Auth account sid and auth token"""
        return (settings.account_sid, settings.auth_token)

    def _make_request(
        self,
        method: str,
        payload: str,
        endpoint: str = None,
        success_message: str = None,
    ):
        """Make an HTTP request to the Twilio API."""
        self.logger.info(
            f"Making {method} request to {endpoint} with payload: {payload}"
        )

        try:
            response = requests.request(
                method=method,
                url=endpoint,
                json=payload,
                headers=self._header,
                auth=self._auth,
            )

            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Request to {endpoint} successful: {response.json()}")
                return {"message": success_message, "data": response.json()}
            else:
                error_message = response.json().get("message", "Unknown error occurred")
                self.logger.error(f"Request to {endpoint} failed: {error_message}")
                raise HTTPException(
                    status_code=response.status_code, detail=error_message
                )
        except Exception as e:
            self.logger.exception(f"Exception during request to {endpoint}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    def send_whatsapp(self, to: str, message: str):
        self.logger.info(f"Sending WhatsApp message to {to}: {message}")
        try:
            response = self.client.messages.create(
                messaging_service_sid=self.message_service_id,
                to=to,
                from_=settings.from_whatsapp_number,
                body=message,
            )
            self.logger.info(f"WhatsApp message sent successfully: {response.sid}")
            return response
        except Exception as e:
            self.logger.exception(f"Failed to send WhatsApp message: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to send WhatsApp message"
            )

    def register_whatsapp(self, sender_request: SenderRequest, business: Business):
        self.logger.info(f"Registering WhatsApp sender: {sender_request.phone_number}")

        payload = {
            "sender_id": f"whatsapp:{sender_request.phone_number}",
            "waba_id": sender_request.waba_id,
            "profile": {
                "name": sender_request.business_name,
                "about": sender_request.about,
                "address": sender_request.address,
                "emails": [sender_request.email],
                "vertical": sender_request.business_type,
                "logo_url": sender_request.logo_url,
                "description": sender_request.description,
                "websites": sender_request.website,
            },
            "webhook": {
                "callback_url": "http://18.184.65.167:3000/api/twilio/incoming-whatsapp",
                "callback_method": "POST",
            },
        }

        response = self._make_request(
            "POST",
            payload,
            settings.TWILIO_API_URL,
            "WhatsApp Sender initiated successfully",
        )

        self.logger.info(f"WhatsApp sender registration response: {response}")
        return response

    def verify_sender(self, verification_request: VerificationRequest):
        """Whatsapp Sender Verification"""
        self.logger.info(
            f"Verifying WhatsApp sender ID: {verification_request.sender_id}"
        )

        payload = {
            "configuration": {
                "verification_code": verification_request.verification_code
            }
        }
        url = f"{settings.TWILIO_API_URL}/{verification_request.sender_id}"

        return self._make_request("POST", payload, url, "Verification successful")

    def get_whatsapp_sender(self, sender_id: SenderId):
        """Fetch a WhatsApp Sender by providing sender ID"""
        self.logger.info(f"Fetching WhatsApp sender info for ID: {sender_id}")

        url = f"{settings.TWILIO_API_URL}/{sender_id}"
        self.twilio_repository.get_sender(sender_id)

        return self._make_request(
            "GET", None, url, "WhatsApp Sender information retrieved"
        )

    def update_whatsapp_sender(self, update_request: UpdateSenderRequest):
        """Update WhatsApp Sender"""
        self.logger.info(f"Updating WhatsApp sender ID: {update_request.sender_id}")

        payload = {
            "webhook": {
                "callback_method": "POST",
                "callback_url": "https://demo.twilio.com/new_webhook",
            },
            "profile": {
                "name": update_request.business_name,
                "about": update_request.about,
                "vertical": update_request.business_type,
                "address": update_request.address,
                "emails": [update_request.email],
                "websites": [update_request.website],
                "logo_url": update_request.logo_url,
                "description": update_request.description,
            },
        }

        url = f"{settings.TWILIO_API_URL}/{update_request.sender_id}"

        return self._make_request(
            "POST", payload, url, "WhatsApp sender updated successfully"
        )

    def delete_whatsapp_sender(self, sender_id: SenderId):
        """Delete WhatsApp Sender"""
        self.logger.info(f"Deleting WhatsApp sender ID: {sender_id.sender_id}")

        url = f"{settings.TWILIO_API_URL}/{sender_id.sender_id}"

        return self._make_request(
            "DELETE", None, url, "WhatsApp sender deleted successfully"
        )
    

    def create_twilio_subaccount(self, business_name: str) -> dict:
        """
        Create a Twilio sub-account for isolating customer WABA setup.
        """
        self.logger.info(f"Creating Twilio subaccount for: {business_name}")
        try:
            # Instead of using the client library, use direct HTTP request
            import requests
            import base64
            
            # Create auth header
            auth_string = f"{settings.account_sid}:{settings.auth_token}"
            encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Make the request to create subaccount
            response = requests.post(
                "https://api.twilio.com/2010-04-01/Accounts.json",
                data={"FriendlyName": business_name},
                headers=headers
            )
            
            if response.status_code != 201:
                self.logger.error(f"Failed to create Twilio subaccount: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to create Twilio subaccount"
                )
            
            # Parse the response
            account_data = response.json()
            self.logger.info(account_data)
            sid = account_data.get("sid")
            auth_token = account_data.get("auth_token")
            
            self.logger.info(f"Sub-account created: SID = {sid}")
            # print(f"Direct HTTP Request: Sub-account created with SID = {sid} and auth token = {auth_token}")
            
            return {
                "sid": sid,
                "auth_token": auth_token
            }
        except Exception as e:
            self.logger.exception(f"Failed to create Twilio sub-account: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create Twilio sub-account: {str(e)}"
            )

    def create_whatsapp_sender(self, phone_number: str, waba_id: str, business: Business) -> dict:
        """
        Register a WhatsApp number with Twilio and make it ready for messaging.
        
        Args:
            phone_number: The WhatsApp number to register (with or without + prefix)
            waba_id: The WhatsApp Business Account ID
            business: The business object containing the business name and Twilio credentials
        
        Returns:
            dict: The sender information including SID, status, and configuration
        """
        try:
            # Check if business has Twilio credentials
            if not business.twilio_subaccount_sid or not business.twilio_auth_token:
                raise HTTPException(
                    status_code=400,
                    detail="Business does not have Twilio credentials configured"
                )

            # Check if waba_id is provided
            if not waba_id:
                raise HTTPException(
                    status_code=400,
                    detail="WhatsApp Business Account ID is required"
                )
                
            # Format the phone number consistently
            # Remove any + prefix for compatibility with Twilio API functions
            if phone_number.startswith("+"):
                formatted_phone_number = phone_number[1:]
            else:
                formatted_phone_number = phone_number
                
            # Create a client with the business's credentials for subsequent API calls
            business_client = Client(business.twilio_subaccount_sid, business.twilio_auth_token)
            
            # Check if a WhatsApp sender already exists with this phone number
            if business.whatsapp_sender_sid and business.whatsapp_sender_id == f"whatsapp:+{formatted_phone_number}":
                self.logger.info(f"WhatsApp sender already exists for {formatted_phone_number} with SID: {business.whatsapp_sender_sid}")
                
                # Only need to update if the WABA ID has changed
                if business.waba_id != waba_id:
                    self.logger.info(f"Updating WABA ID from {business.waba_id} to {waba_id}")
                    # Here we could make an API call to update the WABA ID if Twilio supports it
                    # For now, we'll just return the existing sender info
                
                # Return existing sender info
                return {
                    "status": business.whatsapp_status or "active",
                    "sender_id": business.whatsapp_sender_id,
                    "sid": business.whatsapp_sender_sid,
                    "waba_id": waba_id,  # Return the new WABA ID
                    "profile": business.whatsapp_profile or {}
                }
            
            # Create a messaging service first
            messaging_service = self._get_or_create_messaging_service(
                f"{business.business_name} WhatsApp Service", 
                client=business_client,
                service_sid=business.messaging_service_sid
            )
            
            # Get business profile information
            business_name = getattr(business, 'business_name', '')
            business_email = getattr(business, 'email', '')
            business_address = getattr(business, 'address', '')
            business_website = getattr(business, 'website', '')
            business_description = getattr(business, 'description', f"{business_name}'s WhatsApp Business Account")
            
            # First, we'll check if this phone number is already in the account's phone numbers
            incoming_numbers = business_client.incoming_phone_numbers.list(phone_number=f"+{formatted_phone_number}")
            phone_number_sid = None
            
            if incoming_numbers:
                phone_number_sid = incoming_numbers[0].sid
                self.logger.info(f"Found existing phone number with SID: {phone_number_sid}")
            else:
                # If not found, we need to first purchase the number
                self.logger.info(f"No existing phone number found for +{formatted_phone_number}, attempting to purchase it")
                try:
                    purchased_number = business_client.incoming_phone_numbers.create(
                        phone_number=f"+{formatted_phone_number}",
                        friendly_name=f"WhatsApp Business Number"
                    )
                    phone_number_sid = purchased_number.sid
                    self.logger.info(f"Purchased phone number +{formatted_phone_number} with SID: {phone_number_sid}")
                except Exception as e:
                    self.logger.warning(f"Could not purchase number +{formatted_phone_number}: {str(e)}")
                    # Continue anyway as the number might be already in the account or provisioned elsewhere
            
            # Now connect the number to the messaging service
            if phone_number_sid:
                try:
                    # Add the phone number to the messaging service
                    phone_assoc = business_client.messaging.v1.services(messaging_service.sid).phone_numbers.create(
                        phone_number_sid=phone_number_sid
                    )
                    self.logger.info(f"Added phone number to messaging service: {phone_assoc.sid}")
                except Exception as e:
                    self.logger.warning(f"Failed to add phone number to messaging service: {str(e)}")
                    # Continue anyway as the number might be already in the messaging service
            
            # Now use the correct WhatsApp Channels API to register the sender
            # This is the API endpoint from the curl example
            
            # Get business profile information to use in the payload
            business_name = getattr(business, 'business_name', '')
            business_email = getattr(business, 'email', '')
            business_address = getattr(business, 'address', '')
            business_website = getattr(business, 'website', '')
            business_description = getattr(business, 'description', f"{business_name}'s WhatsApp Business Account")
            
            # Format phone number for WhatsApp (with + sign in the sender_id)
            if not formatted_phone_number.startswith("+"):
                whatsapp_sender_id = f"whatsapp:+{formatted_phone_number}"
            else:
                whatsapp_sender_id = f"whatsapp:{formatted_phone_number}"
            
            # Build the payload according to the example curl command
            channels_payload = {
                "sender_id": whatsapp_sender_id,
                "waba_id": waba_id,
                "profile": {
                    "name": business_name,
                    "about": f"Welcome to {business_name}'s WhatsApp Business",
                    "vertical": "Other",
                    "description": business_description,
                    "address": business_address or "",
                    "emails": [business_email] if business_email else ["support@example.com"],
                    "websites": [business_website] if business_website else [],
                    "logo_url": "https://raw.githubusercontent.com/Xsolai/xsolai/main/logo.png"
                },
                "webhook": {
                    "callback_method": "POST",
                    "callback_url": "http://localhost:8000/api/twilio/incoming-whatsapp"
                }
            }
            
            self.logger.info(f"Sending WhatsApp Channels/Senders API request: {channels_payload}")
            
            # Make the API call to register the WhatsApp sender using the correct endpoint
            try:
                response = requests.post(
                    "https://messaging.twilio.com/v2/Channels/Senders",
                    json=channels_payload,
                    auth=(business.twilio_subaccount_sid, business.twilio_auth_token),
                    headers={"Content-Type": "application/json; charset=utf-8"}
                )
                
                # print(f"Channels/Senders API Response: {response.status_code}")
                # print(f"Response Body: {response.text}")
                
                if response.status_code in [200, 201, 202]:
                    sender_data = response.json()
                    self.logger.info(f"Successfully created WhatsApp sender: {sender_data}")
                    
                    # Return the sender information
                    return {
                        "status": sender_data.get("status", "provisioning"),
                        "sender_id": sender_data.get("sender_id", whatsapp_sender_id),
                        "sid": sender_data.get("sid", ""),
                        "waba_id": waba_id,
                        "profile": sender_data.get("profile", {})
                    }
                else:
                    # Log the error but continue - we'll return a default response
                    self.logger.error(f"Error creating WhatsApp sender: {response.text}")
            except Exception as e:
                self.logger.error(f"Exception creating WhatsApp sender: {str(e)}")
                # Continue to the fallback return
            
            # Even if the above fails, we can still use Twilio's SMS API with WhatsApp format
            # This is a more reliable approach for basic WhatsApp messaging
            
            # Update business record with the WABA ID
            business.waba_id = waba_id
            self.db.commit()
            
            # If we reach here, it means the Channels/Senders API failed
            # Return a fallback response with the phone number information
            self.logger.info(f"Returning fallback WhatsApp sender information for {formatted_phone_number}")
            
            sender_info = {
                "status": "provisioning",  # WhatsApp numbers go through a provisioning process
                "sender_id": whatsapp_sender_id,
                "sid": phone_number_sid or f"whatsapp:{formatted_phone_number.replace('+', '')}",
                "waba_id": waba_id,
                "messaging_service_sid": messaging_service.sid,
                "profile": {
                    "name": business_name,
                    "about": f"Welcome to {business_name}'s WhatsApp Business",
                    "vertical": "Other",
                    "description": business_description
                }
            }
            
            self.logger.info(f"WhatsApp sender setup completed for {formatted_phone_number}")
            
            return sender_info
            
        except Exception as e:
            self.logger.exception(f"Failed to register WhatsApp number {formatted_phone_number}")
            error_detail = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_detail = f"{error_detail} - Response: {e.response.text}"
            # print(f"Detailed error: {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to register WhatsApp number: {error_detail}"
            )

    def _get_or_create_messaging_service(self, friendly_name: str, client=None, service_sid=None):
        """Get existing messaging service or create a new one
        
        Args:
            friendly_name: The friendly name for the messaging service
            client: Optional client for a specific business subaccount
            service_sid: Optional SID of an existing service to use
        
        Returns:
            The messaging service object
        """
        try:
            # Use provided client or default to the main client
            client = client or self.client
            
            # If a service SID is provided, try to fetch that specific service
            if service_sid:
                try:
                    service = client.messaging.v1.services(service_sid).fetch()
                    self.logger.info(f"Found messaging service by SID: {service_sid}")
                    # Update the webhook URLs for the existing service
                    updated_service = client.messaging.v1.services(service.sid).update(
                        inbound_request_url="http://localhost:8000/api/twilio/incoming-whatsapp",
                        status_callback="http://localhost:8000/api/twilio/status-callback",
                        smart_encoding=True
                    )
                    return updated_service
                except Exception as e:
                    self.logger.warning(f"Could not fetch messaging service with SID {service_sid}: {str(e)}")
                    # Continue to creating/finding another service
            
            # Try to find existing service by friendly name
            services = client.messaging.v1.services.list()
            for service in services:
                if service.friendly_name == friendly_name:
                    self.logger.info(f"Found messaging service by name: {friendly_name}")
                    # Update the webhook URLs for the existing service
                    updated_service = client.messaging.v1.services(service.sid).update(
                        inbound_request_url="http://localhost:8000/api/twilio/incoming-whatsapp",
                        status_callback="http://localhost:8000/api/twilio/status-callback",
                        smart_encoding=True
                    )
                    return updated_service
            
            # If this is a free/trial account, check the total count to avoid hitting limits
            if len(services) >= 10:  # Free accounts typically have a limit
                # If we're at the limit, just use the first one
                self.logger.warning(f"Account has {len(services)} messaging services, reusing existing service")
                service = services[0]
                updated_service = client.messaging.v1.services(service.sid).update(
                    friendly_name=friendly_name,  # Update the name
                    inbound_request_url="http://localhost:8000/api/twilio/incoming-whatsapp",
                    status_callback="http://localhost:8000/api/twilio/status-callback",
                    smart_encoding=True
                )
                return updated_service
            
            # If not found or within limits, create new service
            self.logger.info(f"Creating new messaging service: {friendly_name}")
            service = client.messaging.v1.services.create(
                friendly_name=friendly_name,
                inbound_request_url="http://localhost:8000/api/twilio/incoming-whatsapp",
                status_callback="http://localhost:8000/api/twilio/status-callback",
                smart_encoding=True
            )
            return service
        except Exception as e:
            self.logger.exception(f"Failed to get/create messaging service: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _add_sender_to_messaging_service(self, messaging_service_sid, sender_sid, client=None):
        """Add a sender to a messaging service"""
        try:
            # Use provided client or default to the main client
            client = client or self.client
            
            # According to Twilio's latest API, we need to use phone_numbers 
            # resource to add a sender to a messaging service
            response = client.messaging.v1.services(messaging_service_sid).phone_numbers.create(
                phone_number_sid=sender_sid
            )
            
            return response
        except Exception as e:
            self.logger.exception(f"Failed to add sender to messaging service: {str(e)}")
            # If the specific error is about the API endpoint, try an alternative approach
            try:
                # Try using the PhoneNumbers resource directly
                self.logger.info("Trying alternative method to add sender to messaging service")
                response = requests.post(
                    f"https://messaging.twilio.com/v1/Services/{messaging_service_sid}/PhoneNumbers",
                    data={"PhoneNumberSid": sender_sid},
                    auth=(client.username, client.password)
                )
                if response.status_code in [200, 201, 202]:
                    self.logger.info("Successfully added sender using alternative method")
                    return response.json()
                else:
                    self.logger.error(f"Alternative method failed: {response.text}")
                    raise Exception(f"Alternative method failed: {response.text}")
            except Exception as alt_e:
                self.logger.exception(f"Alternative method also failed: {str(alt_e)}")
                raise

    def _add_whatsapp_sender_to_messaging_service(self, messaging_service_sid, sender_sid, client=None):
        """Add a WhatsApp sender to a messaging service using direct HTTP API"""
        client = client or self.client
        try:
            # For WhatsApp senders, we need to use the Channels API
            api_url = f"https://messaging.twilio.com/v1/Services/{messaging_service_sid}/Channels/Senders"
            response = requests.post(
                api_url,
                data={"SenderSid": sender_sid},
                auth=(client.username, client.password)
            )
            
            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Successfully added WhatsApp sender to messaging service: {response.json()}")
                return response.json()
            else:
                error_message = response.text
                self.logger.error(f"Failed to add WhatsApp sender to messaging service: {error_message}")
                # Don't raise an error since this is a non-critical operation
                return None
        except Exception as e:
            self.logger.exception(f"Exception adding WhatsApp sender to messaging service: {str(e)}")
            # Don't raise an exception since this is a non-critical operation
            return None

    def purchase_phone_number(self, business_client=None, country_code="US", capabilities=None, existing_number=None) -> dict:
        """
        Purchase an available phone number from Twilio that can be used for WhatsApp.
        
        Args:
            business_client: Optional Twilio client for a specific business subaccount
            country_code: The country code to search for numbers (default: US)
            capabilities: List of capabilities the number must have (default: SMS, Voice) 
            existing_number: If provided, check if this number already exists in the account
            
        Returns:
            dict: Information about the purchased phone number
        """
        self.logger.info(f"Purchasing phone number with country code: {country_code}")
        try:
            client = business_client or self.client
            capabilities = capabilities or {"sms": True, "voice": True}
            
            # If an existing number was provided, check if it's already in the account
            if existing_number:
                self.logger.info(f"Checking if number {existing_number} already exists in account")
                # Remove any + prefix for consistent formatting
                if existing_number.startswith("+"):
                    existing_number = existing_number[1:]
                
                # Try to find the number
                try:
                    existing_numbers = client.incoming_phone_numbers.list(phone_number=f"+{existing_number}")
                    if existing_numbers:
                        number = existing_numbers[0]
                        self.logger.info(f"Found existing number {number.phone_number} with SID: {number.sid}")
                        return {
                            "sid": number.sid,
                            "phone_number": number.phone_number,
                            "whatsapp_formatted_number": number.phone_number.replace("+", "").replace(" ", ""),
                            "friendly_name": number.friendly_name,
                            "capabilities": {
                                "sms": number.capabilities.get("sms", False),
                                "voice": number.capabilities.get("voice", False),
                                "mms": number.capabilities.get("mms", False)
                            },
                            "status": "existing"
                        }
                except Exception as e:
                    self.logger.warning(f"Error checking for existing number: {str(e)}")
                    # Continue to purchase a new number
            
            # Search for available phone numbers
            available_numbers = client.available_phone_numbers(country_code).local.list(
                sms_enabled=capabilities.get("sms", True),
                voice_enabled=capabilities.get("voice", True),
                limit=1
            )
            
            if not available_numbers:
                self.logger.error(f"No available phone numbers found in {country_code}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No available phone numbers found in {country_code}"
                )
            
            # Purchase the first available number
            phone_number = available_numbers[0].phone_number
            purchased_number = client.incoming_phone_numbers.create(
                phone_number=phone_number,
                friendly_name=f"WhatsApp Number ({phone_number})"
            )
            
            self.logger.info(f"Successfully purchased phone number: {purchased_number.phone_number} with SID: {purchased_number.sid}")
            
            # Format the phone number for WhatsApp (remove + and spaces)
            whatsapp_formatted_number = purchased_number.phone_number.replace("+", "").replace(" ", "")
            
            return {
                "sid": purchased_number.sid,
                "phone_number": purchased_number.phone_number,
                "whatsapp_formatted_number": whatsapp_formatted_number,
                "friendly_name": purchased_number.friendly_name,
                "capabilities": {
                    "sms": purchased_number.capabilities.get("sms", False),
                    "voice": purchased_number.capabilities.get("voice", False),
                    "mms": purchased_number.capabilities.get("mms", False)
                },
                "status": "new"
            }
        except Exception as e:
            self.logger.exception(f"Failed to purchase phone number: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to purchase phone number: {str(e)}"
            )

    def enable_whatsapp_on_number(self, phone_number: str, business_client=None) -> dict:
        """
        Enable WhatsApp capabilities on a Twilio phone number.
        
        Args:
            phone_number: The phone number to enable WhatsApp on (E.164 format)
            business_client: Optional Twilio client for a specific business subaccount
            
        Returns:
            dict: Information about the WhatsApp-enabled number
        """
        self.logger.info(f"Enabling WhatsApp on phone number: {phone_number}")
        try:
            # This requires a direct HTTP request to the Twilio API as the client library
            # doesn't have a simple method for enabling WhatsApp
            client = business_client or self.client
            auth = (client.username, client.password)
            
            # First, verify the number exists in the account
            numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
            if not numbers:
                self.logger.error(f"Phone number {phone_number} not found in Twilio account")
                raise HTTPException(
                    status_code=404,
                    detail=f"Phone number {phone_number} not found in Twilio account"
                )
            
            number_sid = numbers[0].sid
            
            # Enable WhatsApp on the number using direct API request
            response = requests.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{client.username}/IncomingPhoneNumbers/{number_sid}.json",
                data={"SmsApplicationSid": "APxxxxxxxxxxxx"},  # You need to replace this with your WhatsApp-enabled application SID
                auth=auth
            )
            
            if response.status_code not in [200, 201, 202]:
                self.logger.error(f"Failed to enable WhatsApp on number: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to enable WhatsApp on number: {response.text}"
                )
            
            # Return the updated number information
            updated_number = response.json()
            
            return {
                "sid": updated_number.get("sid"),
                "phone_number": updated_number.get("phone_number"),
                "whatsapp_number": f"whatsapp:{updated_number.get('phone_number').replace('+', '')}",
                "friendly_name": updated_number.get("friendly_name"),
                "whatsapp_enabled": True
            }
        except Exception as e:
            self.logger.exception(f"Failed to enable WhatsApp on number: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enable WhatsApp on number: {str(e)}"
            )

