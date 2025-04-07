from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship


class ServicesModel(Base):
    __tablename__ = "Services"
    id = Column(Integer, primary_key=True, index=True)
    item_no = Column(Integer, nullable=True, index=True)
    item_name = Column(String, nullable=True, index=True)
    min_price = Column(Float, nullable=True, index=True)
    bookings = relationship("BookingDetail", back_populates="service")
