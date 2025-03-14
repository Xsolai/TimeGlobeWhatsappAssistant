from .base import Base
from sqlalchemy import Column, String, Integer


class CustomerModel(Base):
    __tablename__ = "Customers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    mobile_number = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    gender = Column(String, nullable=True)
