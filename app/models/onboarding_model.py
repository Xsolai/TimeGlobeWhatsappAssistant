from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from enum import Enum as PyEnum

Base = declarative_base()

class WABAStatus(PyEnum):
    pending = "pending"
    connected = "connected"
    failed = "failed"

class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    twilio_subaccount_sid = Column(String, nullable=False)
    twilio_auth_token = Column(String, nullable=False)
    whatsapp_number = Column(String, nullable=True)
    waba_status = Column(Enum(WABAStatus), default=WABAStatus.pending)
