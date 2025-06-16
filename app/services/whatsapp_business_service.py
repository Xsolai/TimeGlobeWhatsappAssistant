import requests
import json
from typing import Optional, Dict, Any
from ..core.config import settings
from ..models.business_model import Business
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..logger import main_logger


class WhatsAppBusinessService:
    """
    Direct WhatsApp Business API integration service.
    Replaces Dialog360Service with Meta's official WhatsApp Business API.
    """
    
    def __init__(self, db: Session):
        self.logger = main_logger
        self.db = db
        self.base_url = "https://graph.facebook.com/v18.0"

    def _get_business_by_phone(self, phone_number: str) -> Optional[Business]:
        """
        Get the business information based on the phone number.
        Used to retrieve API credentials from DB.
        """
        # Normalize phone number for comparison
        normalized_phone = phone_number
        if phone_number.startswith("whatsapp:"):
            normalized_phone = phone_number.replace("whatsapp:", "")
        
        self.logger.info(f"Looking for business with number: {normalized_phone}")
        
        try:
            # Create multiple formats to try matching
            formats_to_try = []
            
            # If number already has +, try both with and without
            if normalized_phone.startswith("+"):
                formats_to_try.append(normalized_phone)                  # +923463109994
                formats_to_try.append(normalized_phone[1:])              # 923463109994
            else:
                formats_to_try.append(normalized_phone)                  # 923463109994
                formats_to_try.append(f"+{normalized_phone}")            # +923463109994
            
            self.logger.info(f"Trying to match against formats: {formats_to_try}")
            
            # Try each format
            for phone_format in formats_to_try:
                business = self.db.query(Business).filter(Business.whatsapp_number == phone_format).first()
                if business:
                    self.logger.info(f"Found business with number format: {phone_format}")
                    return business
            
            # If we got here, no match was found
            self.logger.warning(f"No business found with any of these WhatsApp number formats: {formats_to_try}")
            
        except Exception as e:
            self.logger.exception(f"Error finding business by whatsapp_number: {str(e)}")
            return None
        
        return None

    def _get_api_headers(self, business: Business) -> Dict[str, str]:
        """Return API headers for WhatsApp Business API requests."""
        if not business or not business.api_key:
            raise HTTPException(status_code=400, detail="No API key found for business")
        
        return {
            "Authorization": f"Bearer {business.api_key}",
            "Content-Type": "application/json"
        }

    def _get_phone_number_id(self, business: Business) -> str:
        """Get the phone number ID for WhatsApp Business API."""
        if not business or not business.channel_id:
            raise HTTPException(status_code=400, detail="No phone number ID found for business")
        
        # In direct WhatsApp Business API, channel_id stores the phone_number_id
        return business.channel_id

    def send_message(self, to: str, message: str, business_phone: str) -> Dict[str, Any]:
        """
        Send a WhatsApp message using Meta's WhatsApp Business API.
        
        Args:
            to: Recipient phone number
            message: Message text to send
            business_phone: Business phone number (sender)
            
        Returns:
            Dict containing response data
        """
        # Format recipient number without "whatsapp:" prefix
        if to.startswith("whatsapp:"):
            to = to.replace("whatsapp:", "")
        
        # Ensure number has country code
        if not to.startswith("+"):
            to = f"+{to}"
        
        self.logger.info(f"Sending WhatsApp message to {to}: {message}")
        
        try:
            # Get the business record
            business = self._get_business_by_phone(business_phone)
            if not business:
                raise HTTPException(status_code=400, detail="Invalid business phone number")
            
            # Get phone number ID and headers
            phone_number_id = self._get_phone_number_id(business)
            headers = self._get_api_headers(business)
            
            # Construct the message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            # WhatsApp Business API endpoint
            url = f"{self.base_url}/{phone_number_id}/messages"
            
            self.logger.info(f"Making request to: {url}")
            self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                self.logger.info(f"WhatsApp message sent successfully: {response_data}")
                return {
                    "success": True,
                    "message": "Message sent successfully",
                    "data": response_data
                }
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                self.logger.error(f"Failed to send WhatsApp message. Status: {response.status_code}, Error: {error_message}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to send message: {error_message}"
                )
                
        except Exception as e:
            self.logger.exception(f"Error sending WhatsApp message: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send WhatsApp message: {str(e)}"
            )

    def verify_webhook(self, verify_token: str, challenge: str) -> str:
        """
        Verify webhook for WhatsApp Business API.
        
        Args:
            verify_token: Token to verify
            challenge: Challenge string from Facebook
            
        Returns:
            Challenge string if verification successful
        """
        # Use the configured webhook verify token
        expected_token = settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN
        
        if verify_token == expected_token:
            self.logger.info("Webhook verification successful")
            return challenge
        else:
            self.logger.error(f"Webhook verification failed. Expected: {expected_token}, Got: {verify_token}")
            raise HTTPException(status_code=403, detail="Webhook verification failed")

    def get_business_profile(self, business_phone: str) -> Dict[str, Any]:
        """
        Get WhatsApp Business profile information.
        
        Args:
            business_phone: Business phone number
            
        Returns:
            Dict containing profile information
        """
        try:
            business = self._get_business_by_phone(business_phone)
            if not business:
                raise HTTPException(status_code=400, detail="Invalid business phone number")
            
            phone_number_id = self._get_phone_number_id(business)
            headers = self._get_api_headers(business)
            
            # WhatsApp Business API endpoint for business profile
            url = f"{self.base_url}/{phone_number_id}/whatsapp_business_profile"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                self.logger.info(f"Retrieved business profile: {profile_data}")
                return profile_data
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                self.logger.error(f"Failed to get business profile. Status: {response.status_code}, Error: {error_message}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get business profile: {error_message}"
                )
                
        except Exception as e:
            self.logger.exception(f"Error getting business profile: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get business profile: {str(e)}"
            )

    def update_business_profile(self, business_phone: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update WhatsApp Business profile information.
        
        Args:
            business_phone: Business phone number
            profile_data: Profile data to update
            
        Returns:
            Dict containing response data
        """
        try:
            business = self._get_business_by_phone(business_phone)
            if not business:
                raise HTTPException(status_code=400, detail="Invalid business phone number")
            
            phone_number_id = self._get_phone_number_id(business)
            headers = self._get_api_headers(business)
            
            # WhatsApp Business API endpoint for updating business profile
            url = f"{self.base_url}/{phone_number_id}/whatsapp_business_profile"
            
            response = requests.post(url, headers=headers, json=profile_data)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                self.logger.info(f"Business profile updated successfully: {response_data}")
                return response_data
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                self.logger.error(f"Failed to update business profile. Status: {response.status_code}, Error: {error_message}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to update business profile: {error_message}"
                )
                
        except Exception as e:
            self.logger.exception(f"Error updating business profile: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update business profile: {str(e)}"
            )

    def get_phone_numbers(self, waba_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get phone numbers associated with a WhatsApp Business Account.
        
        Args:
            waba_id: WhatsApp Business Account ID
            access_token: Access token for the WABA
            
        Returns:
            Dict containing phone numbers data
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/{waba_id}/phone_numbers"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                phone_data = response.json()
                self.logger.info(f"Retrieved phone numbers: {phone_data}")
                return phone_data
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                self.logger.error(f"Failed to get phone numbers. Status: {response.status_code}, Error: {error_message}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get phone numbers: {error_message}"
                )
                
        except Exception as e:
            self.logger.exception(f"Error getting phone numbers: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get phone numbers: {str(e)}"
            )

    # Legacy method name compatibility
    def send_whatsapp(self, to: str, message: str, business_phone: str) -> Dict[str, Any]:
        """Legacy method name for backward compatibility."""
        return self.send_message(to, message, business_phone) 