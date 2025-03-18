from .base import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime


class BookingDetail(Base):
    __tablename__ = "BookingDetails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    begin_ts = Column(DateTime, nullable=False)
    duration_millis = Column(BigInteger, nullable=False)
    employee_id = Column(Integer, nullable=False)
    item_no = Column(Integer, nullable=False)
    item_nm = Column(String, nullable=True)
    book_id = Column(Integer, ForeignKey("BookedAppointment.id"), nullable=False)
    book = relationship("BookModel", back_populates="booking_details")
