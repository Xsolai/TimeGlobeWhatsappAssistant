from .base import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime


class BookingDetail(Base):
    __tablename__ = "BookingDetails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    begin_ts = Column(DateTime, nullable=False)
    duration_millis = Column(BigInteger, nullable=False)
    employee_id = Column(Integer, nullable=True)
    item_no = Column(Integer, ForeignKey("Services.item_no"), nullable=True)
    book_id = Column(Integer, ForeignKey("BookedAppointment.id"), nullable=False)
    book = relationship("BookModel", back_populates="booking_details")
    service = relationship("ServicesModel", back_populates="bookings")
