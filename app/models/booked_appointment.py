from .base import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship


class BookModel(Base):
    __tablename__ = "BookedAppointment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_cd = Column(String, nullable=False)
    site_cd = Column(String, nullable=False)
    booking_details = relationship("BookingDetail", back_populates="book")
