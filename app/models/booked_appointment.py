from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class BookModel(Base):
    __tablename__ = "BookedAppointment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, unique=True, index=True)
    site_cd = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("Customers.id"), nullable=False)
    business_phone_number = Column(String, nullable=True)

    booking_details = relationship("BookingDetail", back_populates="book")
    customer = relationship("CustomerModel", back_populates="appointments")
