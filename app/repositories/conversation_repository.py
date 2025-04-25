from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import json
from ..models.conversation_model import ConversationHistory
import logging

logger = logging.getLogger(__name__)

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation_history(self, mobile_number: str) -> Optional[List[Dict]]:
        """
        Retrieve conversation history for a user.
        Returns a list of message dictionaries or None if not found.
        """
        try:
            history = self.db.query(ConversationHistory).filter(
                ConversationHistory.mobile_number == mobile_number
            ).first()
            
            if not history:
                logger.info(f"No conversation history found for user {mobile_number}")
                return None
                
            return history.messages
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return None

    def save_conversation_history(self, mobile_number: str, messages: List[Dict]) -> bool:
        """
        Save conversation history for a user.
        Returns True if successful, False otherwise.
        """
        try:
            history = self.db.query(ConversationHistory).filter(
                ConversationHistory.mobile_number == mobile_number
            ).first()
            
            if history:
                # Update existing history
                history.messages = messages
            else:
                # Create new history
                history = ConversationHistory(
                    mobile_number=mobile_number,
                    messages=messages
                )
                self.db.add(history)
                
            self.db.commit()
            logger.info(f"Saved conversation history for user {mobile_number}, length: {len(messages)}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving conversation history: {str(e)}")
            return False

    def delete_conversation_history(self, mobile_number: str) -> bool:
        """
        Delete conversation history for a user.
        Returns True if successful, False otherwise.
        """
        try:
            history = self.db.query(ConversationHistory).filter(
                ConversationHistory.mobile_number == mobile_number
            ).first()
            
            if history:
                self.db.delete(history)
                self.db.commit()
                logger.info(f"Deleted conversation history for user {mobile_number}")
                return True
            
            logger.info(f"No conversation history found to delete for user {mobile_number}")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting conversation history: {str(e)}")
            return False 