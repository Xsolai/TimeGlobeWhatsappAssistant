from sqlalchemy import Column, String, Enum, Boolean, DateTime, JSON
import uuid
from enum import Enum as PyEnum
from datetime import datetime, timezone
from .base import Base
from sqlalchemy.orm import relationship

class WABAStatus(PyEnum):
    pending = "pending"
    connected = "connected"
    failed = "failed"

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Twilio fields
    twilio_subaccount_sid = Column(String, nullable=True)
    twilio_auth_token = Column(String(255), nullable=True)
    whatsapp_number = Column(String, nullable=True)
    phone_number_sid = Column(String, nullable=True)  # To store the purchased phone number SID
    messaging_service_sid = Column(String, nullable=True)  # To store the Twilio messaging service SID
    waba_status = Column(Enum(WABAStatus), default=WABAStatus.pending)
    
    # WhatsApp Sender fields
    whatsapp_sender_sid = Column(String, nullable=True)
    whatsapp_sender_id = Column(String, nullable=True)
    waba_id = Column(String, nullable=True)
    whatsapp_status = Column(String, nullable=True)
    whatsapp_profile = Column(JSON, nullable=True)

    # Relationships
    whatsapp_sender = relationship("WASenderModel", back_populates="business", uselist=False)
    subscriptions = relationship("BusinessSubscription", back_populates="business")
