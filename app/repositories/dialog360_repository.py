from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.sender_model import WASenderModel
from ..schemas.dialog360_sender import SenderId


class Dialog360Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_sender(self, sender_id: str):
        """Get a sender by ID"""
        return (
            self.db.query(WASenderModel)
            .filter(
                or_(
                    WASenderModel.sender_id == sender_id,
                    WASenderModel.phone_number == sender_id,
                )
            )
            .first()
        )

    def create_sender(self, **kwargs):
        """Create a new sender record"""
        sender = WASenderModel(**kwargs)
        self.db.add(sender)
        self.db.commit()
        self.db.refresh(sender)
        return sender

    def update_sender(self, sender_id: str, **kwargs):
        """Update a sender record"""
        sender = self.get_sender(sender_id)
        if sender:
            for key, value in kwargs.items():
                setattr(sender, key, value)
            self.db.commit()
            self.db.refresh(sender)
        return sender

    def delete_sender(self, sender_id: str):
        """Delete a sender record"""
        sender = self.get_sender(sender_id)
        if sender:
            self.db.delete(sender)
            self.db.commit()
        return sender 