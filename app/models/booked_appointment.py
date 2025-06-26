from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .appointment_status import AppointmentStatus

class BookModel(Base):
    __tablename__ = "BookedAppointment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, unique=True, index=True)
    site_cd = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("Customers.id"), nullable=False, index=True)
    business_phone_number = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.BOOKED, nullable=False)

    booking_details = relationship("BookingDetail", back_populates="book")
    customer = relationship("CustomerModel", back_populates="appointments")

    __table_args__ = (
        Index('idx_appointment_business_date', 'business_phone_number', 'created_at'),
        Index('idx_appointment_customer_date', 'customer_id', 'created_at'),
    )
