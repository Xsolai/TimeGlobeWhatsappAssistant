from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..schemas.onboarding import (
    BusinessDetails,
    WhatsAppConnection,
    BookingPreferences,
    OnboardingStep,
    OnboardingStatus,
    OnboardingResponse
)
from ..services.twilio_service import TwilioService
from ..repositories.user_repository import UserRepository
from ..repositories.onboarding_repository import OnboardingRepository
from ..logger import main_logger

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.twilio_service = TwilioService(db)
        self.user_repository = UserRepository(db)
        self.onboarding_repository = OnboardingRepository(db)

    async def save_business_details(
        self,
        user_id: int,
        business_details: BusinessDetails
    ) -> OnboardingResponse:
        try:
            # Create Twilio sub-account
            sub_account = self.twilio_service.create_twilio_subaccount(
                business_details.business_name
            )
            
            # Save business details and sub-account info
            self.onboarding_repository.save_business_details(
                user_id=user_id,
                business_details=business_details,
                twilio_subaccount_sid=sub_account["sid"],
                twilio_auth_token=sub_account["auth_token"]
            )

            return OnboardingResponse(
                status="success",
                message="Business details saved successfully",
                data={
                    "step": OnboardingStep.BUSINESS_DETAILS,
                    "completed": True
                }
            )
        except Exception as e:
            main_logger.exception(f"Failed to save business details: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save business details"
            )

    async def connect_whatsapp(
        self,
        user_id: int,
        whatsapp_connection: WhatsAppConnection
    ) -> OnboardingResponse:
        try:
            # Get user's Twilio sub-account info
            sub_account_info = self.onboarding_repository.get_twilio_subaccount(user_id)
            
            # Create WhatsApp sender in the sub-account
            sender_sid = self.twilio_service.create_whatsapp_sender(
                phone_number=whatsapp_connection.phone_number,
                friendly_name=sub_account_info["business_name"]
            )

            # Save WhatsApp connection details
            self.onboarding_repository.save_whatsapp_connection(
                user_id=user_id,
                whatsapp_connection=whatsapp_connection,
                sender_sid=sender_sid
            )

            return OnboardingResponse(
                status="success",
                message="WhatsApp connection established successfully",
                data={
                    "step": OnboardingStep.WHATSAPP_CONNECT,
                    "completed": True
                }
            )
        except Exception as e:
            main_logger.exception(f"Failed to connect WhatsApp: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to connect WhatsApp"
            )

    async def save_booking_preferences(
        self,
        user_id: int,
        booking_preferences: BookingPreferences
    ) -> OnboardingResponse:
        try:
            # Save booking preferences
            self.onboarding_repository.save_booking_preferences(
                user_id=user_id,
                booking_preferences=booking_preferences
            )

            return OnboardingResponse(
                status="success",
                message="Booking preferences saved successfully",
                data={
                    "step": OnboardingStep.BOOKING_SETUP,
                    "completed": True
                }
            )
        except Exception as e:
            main_logger.exception(f"Failed to save booking preferences: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save booking preferences"
            )

    async def get_onboarding_status(self, user_id: int) -> OnboardingStatus:
        try:
            return self.onboarding_repository.get_onboarding_status(user_id)
        except Exception as e:
            main_logger.exception(f"Failed to get onboarding status: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get onboarding status"
            ) 