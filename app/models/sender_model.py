from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class SenderModel(Base):
    __tablename__ = "WhatsAppSenders"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    business_name = Column(String)
    about = Column(String)
    description = Column(String)
    address = Column(String)
    business_type = Column(String)
    email = Column(String)
    website = Column(String)
    logo_url = Column(String)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    user = relationship("UserModel", back_populates="whatsapp_sender")
    appointments = relationship("BookModel", back_populates="sender")
