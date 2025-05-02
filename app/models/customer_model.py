from .base import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class CustomerModel(Base):
    __tablename__ = "Customers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    mobile_number = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True, index=True)
    appointments = relationship("BookModel", back_populates="customer")
    business = relationship("Business", back_populates="customers")
    dplAccepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
