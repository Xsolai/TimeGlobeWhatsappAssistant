from sqlalchemy.orm import Session
from typing import Optional
from ..models.customer_model import CustomerModel
from ..models.sender_model import SenderModel
from ..models.user import UserModel
from ..schemas import twilio_sender, auth
from ..logger import main_logger
from ..models.thread import ThreadModel
from ..schemas import thread
from ..models.active_run import ActiveRunModel


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

    def create_thread(self, thread_data: thread.ThreadCreate):
        """Insert a new thread entry into the database."""
        main_logger.info(
            f"Creating new thread for mobile number: {thread_data.mobile_number}"
        )
        try:
            new_thread = ThreadModel(**thread_data.model_dump())
            self.db.add(new_thread)
            self.db.commit()
            self.db.refresh(new_thread)
            return new_thread
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error creating thread: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_thread_by_number(
        self, mobile_number: str
    ) -> Optional[thread.ThreadResponse]:
        """Retrieve thread by mobile number."""
        main_logger.info(f"Fetching thread for mobile number: {mobile_number}")
        try:
            thread = (
                self.db.query(ThreadModel)
                .filter(ThreadModel.mobile_number == mobile_number)
                .first()
            )
            if not thread:
                main_logger.warning(
                    f"No thread found for mobile number: {mobile_number}"
                )
            return thread
        except Exception as e:
            main_logger.error(f"Error retrieving thread: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_active_run(self, thread_id: str) -> Optional[str]:
        """Retrieve the active run ID for a given thread ID."""
        main_logger.info(f"Fetching active run for thread ID: {thread_id}")
        try:
            active_run = (
                self.db.query(ActiveRunModel)
                .filter(ActiveRunModel.thread_id == thread_id)
                .first()
            )
            return active_run.run_id if active_run else None
        except Exception as e:
            main_logger.error(f"Error retrieving active run: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def store_active_run(self, thread_id: str, run_id: str) -> None:
        """Store the active run for a thread."""
        main_logger.info(f"Storing active run {run_id} for thread ID: {thread_id}")
        try:
            existing_run = (
                self.db.query(ActiveRunModel)
                .filter(ActiveRunModel.thread_id == thread_id)
                .first()
            )

            if existing_run:
                existing_run.run_id = run_id  # Update existing run ID
            else:
                new_run = ActiveRunModel(thread_id=thread_id, run_id=run_id)
                self.db.add(new_run)

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error storing active run: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def delete_active_run(self, thread_id: str) -> None:
        """Delete the active run for a thread."""
        main_logger.info(f"Deleting active run for thread ID: {thread_id}")
        try:
            self.db.query(ActiveRunModel).filter(
                ActiveRunModel.thread_id == thread_id
            ).delete()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error deleting active run: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
