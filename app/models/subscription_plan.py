from sqlalchemy import Column, Integer, String, Float, Boolean
from .base import Base


class SubscriptionPlan(Base):
    __tablename__ = "SubscriptionPlans"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    duration_in_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    trial_days = Column(Integer, default=0)
