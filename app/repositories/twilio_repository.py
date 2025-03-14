from ..models.sender_model import SenderModel
from ..models.user import UserModel
from ..schemas import twilio_sender, auth
from sqlalchemy.orm import Session


class TwilioRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_whatsapp_sender(
        self,
        sender_data: twilio_sender.SenderRequest,
        sender_id: str,
        user: auth.User,
    ):
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
            return sender
        except Exception as e:
            self.db.rollback()
            print(f"excepion==>>{str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_sender(self, sender_id: str) -> twilio_sender.SenderRequest:
        try:
            sender = (
                self.db.query(SenderModel)
                .filter(SenderModel.sender_id == sender_id)
                .first()
            )
            return sender
        except Exception as e:
            self.db.rollback()
            print(f"excepion==>>{str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_sender(
        self, sender_id: str, sender_data: twilio_sender.UpdateSenderRequest
    ):
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
                return sender
            else:
                raise Exception("No sender Found.")
        except Exception as e:
            self.db.rollback()
            print(f"excepion==>>{str(e)}")
            raise Exception(f"Database error: {str(e)}")
