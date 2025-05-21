from ..core.config import settings
import requests

from ..models.business_model import Business
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..logger import main_logger


class Dialog360Service:
    def __init__(self, db: Session):
        self.logger = main_logger
        self.db = db

    def _get_business_by_phone(self, phone_number: str):
        """
        Get the business information based on the phone number.
        Used to retrieve API credentials from DB instead of environment variables.
        """
        # Normalize phone number for comparison
        normalized_phone = phone_number
        if phone_number.startswith("whatsapp:"):
            normalized_phone = phone_number.replace("whatsapp:", "")
        
        self.logger.info(f"Looking for business with number: {normalized_phone}")
        
        # Try to find business by whatsapp_number - try different formats
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
        
        # No fall back, return None
        return None

    def _get_api_header(self, phone_number: str):
        """Return API headers for the business associated with ``phone_number``."""

        if not phone_number:
            raise HTTPException(status_code=400, detail="Business phone is required")

        business = self._get_business_by_phone(phone_number)
        if business and business.api_key:
            self.logger.info(f"Using API key from database for number: {phone_number}")
            return {
                "Content-Type": "application/json",
                "D360-API-KEY": business.api_key,
            }

        # No API key found for this phone number
        raise HTTPException(status_code=400, detail="No API key found for the given phone number")

    def _get_api_endpoint(self, phone_number: str):
        """Return the API endpoint for the business associated with ``phone_number``."""

        if not phone_number:
            raise HTTPException(status_code=400, detail="Business phone is required")

        business = self._get_business_by_phone(phone_number)
        if business and business.api_endpoint:
            return business.api_endpoint

        raise HTTPException(status_code=400, detail="No API endpoint found for the given phone number")

    def _make_request(
        self,
        method: str,
        payload: str,
        endpoint: str = None,
        success_message: str = None,
        phone_number: str = None,
    ):
        """Make an HTTP request to the 360dialog API."""
        self.logger.info(
            f"Making {method} request to {endpoint} with payload: {payload}"
        )

        # Get header with proper API key based on phone number
        headers = self._get_api_header(phone_number)

        try:
            response = requests.request(
                method=method,
                url=endpoint,
                json=payload,
                headers=headers,
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

    def send_whatsapp(self, to: str, message: str, business_phone: str):
        """Send a WhatsApp message using 360dialog Cloud API for the specified business."""
        
        # Format recipient number without "whatsapp:" prefix
        if to.startswith("whatsapp:"):
            to = to.replace("whatsapp:", "")
        self.logger.info(f"Sending WhatsApp message to {to}: {message}")
        # Make sure the number includes country code and starts with +
        if not to.startswith("+"):
            to = f"+{to}"

        try:
            from_business = self._get_business_by_phone(business_phone)
            if not from_business:
                raise HTTPException(status_code=400, detail="Invalid business phone number")
            
            # Construct payload using Cloud API format
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            # Use the Cloud API endpoint from the selected business
            api_endpoint = self._get_api_endpoint(from_business.whatsapp_number)
            
            # Make sure we have the full URL for the messages endpoint
            if not api_endpoint.endswith("/messages"):
                cloud_api_url = f"{api_endpoint}/messages"
            else:
                cloud_api_url = api_endpoint
            
            # Pass the sender's phone number to use the right credentials
            sender_number = from_business.whatsapp_number
            
            response = self._make_request(
                "POST",
                payload,
                cloud_api_url,
                "Message sent successfully",
                sender_number
            )
            
            self.logger.info(f"WhatsApp message sent successfully via 360dialog")
            return response
        except Exception as e:
            self.logger.exception(f"Failed to send WhatsApp message: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to send WhatsApp message"
            )

