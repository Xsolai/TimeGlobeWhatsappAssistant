from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class BookModel(Base):
    __tablename__ = "BookedAppointment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, unique=True, index=True)
    site_cd = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("Customers.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    sender_id = Column(Integer, ForeignKey("WhatsAppSenders.id"), nullable=True)
    booking_details = relationship("BookingDetail", back_populates="book")
    customer = relationship("CustomerModel", back_populates="appointments")
    sender = relationship("SenderModel", back_populates="appointments")
