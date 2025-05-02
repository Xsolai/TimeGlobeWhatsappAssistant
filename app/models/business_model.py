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
    
    # 360dialog WhatsApp Business API fields
    client_id = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    api_endpoint = Column(String, nullable=True)  # This will store the address
    app_id = Column(String, nullable=True)
    waba_status = Column(Enum(WABAStatus), default=WABAStatus.pending)
    whatsapp_profile = Column(JSON, nullable=True)
    whatsapp_number = Column(String, nullable=True)  # Store the WhatsApp number
    
    # TimeGlobe-specific fields
    timeglobe_auth_key = Column(String, nullable=True)
    customer_cd = Column(String, nullable=True)  # Used for API calls to TimeGlobe

    subscriptions = relationship("BusinessSubscription", back_populates="business")
    customers = relationship("CustomerModel", back_populates="business")
