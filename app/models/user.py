from .base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


class UserModel(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)  # ✅ New
    business_name = Column(String)  # ✅ New
    twilio_subaccount_sid = Column(String, nullable=True)
    twilio_subaccount_token = Column(String, nullable=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    whatsapp_sender = relationship(
        "SenderModel",
        uselist=False,
        back_populates="user",
        cascade="all,delete",
    )
    subscriptions = relationship("UserSubscription", back_populates="user")
