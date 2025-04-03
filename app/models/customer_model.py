from .base import Base
from sqlalchemy import Column, String, Integer,Boolean,Integer
from sqlalchemy.orm import relationship


class CustomerModel(Base):
    __tablename__ = "Customers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    mobile_number = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    dpl_accepted = Column(Integer, default=False)  # <-- NEU hinzugefügt
    appointments = relationship("BookModel", back_populates="customer", lazy="joined")

