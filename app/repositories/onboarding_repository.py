from sqlalchemy.orm import Session
from ..schemas.onboarding import (
    BusinessDetails,
    WhatsAppConnection,
    BookingPreferences,
    OnboardingStep,
    OnboardingStatus
)
from ..models.onboarding import (
    BusinessProfile,
    WhatsAppConnection as WhatsAppConnectionModel,
    BookingSettings,
    OnboardingProgress
)
from ..logger import main_logger

class OnboardingRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_business_details(
        self,
        business_id: int,
        business_details: BusinessDetails,
        twilio_subaccount_sid: str,
        twilio_auth_token: str
    ) -> None:
        try:
            # Create or update business profile
            business_profile = BusinessProfile(
                business_id=business_id,
                business_name=business_details.business_name,
                location=business_details.location,
                business_email=business_details.business_email,
                website=business_details.website,
                industry=business_details.industry,
                description=business_details.description,
                twilio_subaccount_sid=twilio_subaccount_sid,
                twilio_auth_token=twilio_auth_token
            )
            self.db.add(business_profile)
            self.db.commit()

            # Update onboarding progress
            self._update_onboarding_progress(
                business_id=business_id,
                step=OnboardingStep.BUSINESS_DETAILS,
                completed=True
            )
        except Exception as e:
            self.db.rollback()
            main_logger.exception(f"Failed to save business details: {str(e)}")
            raise

    def save_whatsapp_connection(
        self,
        business_id: int,
        whatsapp_connection: WhatsAppConnection,
        sender_sid: str
    ) -> None:
        try:
            # Create or update WhatsApp connection
            connection = WhatsAppConnectionModel(
                business_id=business_id,
                phone_number=whatsapp_connection.phone_number,
                waba_id=whatsapp_connection.waba_id,
                business_manager_id=whatsapp_connection.business_manager_id,
                sender_sid=sender_sid
            )
            self.db.add(connection)
            self.db.commit()

            # Update onboarding progress
            self._update_onboarding_progress(
                business_id=business_id,
                step=OnboardingStep.WHATSAPP_CONNECT,
                completed=True
            )
        except Exception as e:
            self.db.rollback()
            main_logger.exception(f"Failed to save WhatsApp connection: {str(e)}")
            raise

    def save_booking_preferences(
        self,
        business_id: int,
        booking_preferences: BookingPreferences
    ) -> None:
        try:
            # Create or update booking settings
            booking_settings = BookingSettings(
                business_id=business_id,
                working_hours=booking_preferences.working_hours,
                services=booking_preferences.services,
                welcome_message=booking_preferences.welcome_message,
                faq=booking_preferences.faq
            )
            self.db.add(booking_settings)
            self.db.commit()

            # Update onboarding progress
            self._update_onboarding_progress(
                business_id=business_id,
                step=OnboardingStep.BOOKING_SETUP,
                completed=True
            )
        except Exception as e:
            self.db.rollback()
            main_logger.exception(f"Failed to save booking preferences: {str(e)}")
            raise

    def get_twilio_subaccount(self, business_id: int) -> dict:
        try:
            business_profile = self.db.query(BusinessProfile).filter(
                BusinessProfile.business_id == business_id
            ).first()
            
            if not business_profile:
                raise ValueError("Business profile not found")
            
            return {
                "sid": business_profile.twilio_subaccount_sid,
                "auth_token": business_profile.twilio_auth_token,
                "business_name": business_profile.business_name
            }
        except Exception as e:
            main_logger.exception(f"Failed to get Twilio sub-account: {str(e)}")
            raise

    def get_onboarding_status(self, business_id: int) -> OnboardingStatus:
        try:
            progress = self.db.query(OnboardingProgress).filter(
                OnboardingProgress.business_id == business_id
            ).first()
            
            if not progress:
                return OnboardingStatus(
                    step=OnboardingStep.SIGNUP,
                    completed=False
                )
            
            return OnboardingStatus(
                step=progress.current_step,
                completed=progress.completed,
                data=progress.data
            )
        except Exception as e:
            main_logger.exception(f"Failed to get onboarding status: {str(e)}")
            raise

    def _update_onboarding_progress(
        self,
        business_id: int,
        step: OnboardingStep,
        completed: bool
    ) -> None:
        try:
            progress = self.db.query(OnboardingProgress).filter(
                OnboardingProgress.business_id == business_id
            ).first()
            
            if not progress:
                progress = OnboardingProgress(
                    business_id=business_id,
                    current_step=step,
                    completed=completed
                )
                self.db.add(progress)
            else:
                progress.current_step = step
                progress.completed = completed
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            main_logger.exception(f"Failed to update onboarding progress: {str(e)}")
            raise 