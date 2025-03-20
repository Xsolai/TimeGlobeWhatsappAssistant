from sqlalchemy.orm import Session
from typing import Optional
from ..models.sender_model import SenderModel
from ..models.user import UserModel
from ..schemas import twilio_sender, auth
from ..logger import main_logger


class TwilioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_whatsapp_sender(
        self,
        sender_data: twilio_sender.SenderRequest,
        sender_id: str,
        user: auth.User,
    ):
        main_logger.debug(f"Creating WhatsApp sender for user ID: {user.id}")
        try:
            sender = SenderModel(
                sender_id=sender_id,
                phone_number=sender_data.phone_number,
                business_name=sender_data.business_name,
                address=sender_data.address,
                email=sender_data.email,
                business_type=sender_data.business_type,
                logo_url=str(sender_data.logo_url),
                description=sender_data.description,
                about=sender_data.about,
                website=str(sender_data.website),
                user_id=user.id,
            )
            self.db.add(sender)
            self.db.commit()
            self.db.refresh(sender)
            main_logger.info(
                f"WhatsApp sender created successfully: {sender.sender_id}"
            )
            return sender
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error creating WhatsApp sender: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_sender(self, sender_id: str) -> Optional[twilio_sender.SenderRequest]:
        main_logger.debug(f"Fetching sender with ID: {sender_id}")
        try:
            sender = (
                self.db.query(SenderModel)
                .filter(SenderModel.sender_id == sender_id)
                .first()
            )
            if not sender:
                main_logger.warning(f"Sender not found with ID: {sender_id}")
            else:
                main_logger.info(f"Sender fetched successfully: {sender.sender_id}")
            return sender
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error fetching sender: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_sender(
        self, sender_id: str, sender_data: twilio_sender.UpdateSenderRequest
    ):
        main_logger.debug(f"Updating sender with ID: {sender_id}")
        try:
            sender = self.get_sender(sender_id)
            if sender:
                sender.about = sender_data.about
                sender.description = sender_data.description
                sender.address = sender_data.address
                sender.business_name = sender_data.business_name
                sender.business_type = sender_data.business_type
                sender.email = sender_data.email
                sender.website = sender_data.website
                sender.logo_url = sender_data.logo_url
                self.db.commit()
                self.db.refresh(sender)
                main_logger.info(f"Sender updated successfully: {sender.sender_id}")
                return sender
            else:
                main_logger.warning(f"No sender found with ID: {sender_id}")
                raise Exception("No sender found.")
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error updating sender: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
