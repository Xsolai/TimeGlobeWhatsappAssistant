from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from .base import Base


class BusinessSubscription(Base):
    __tablename__ = "business_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    subscription_plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships (assuming Business and SubscriptionPlan models exist)
    business = relationship("Business", back_populates="subscriptions")
    subscription_plan = relationship("SubscriptionPlan", back_populates="business_subscriptions")

    def activate_subscription(self, duration_days: int):
        """Sets the end date based on subscription duration"""
        self.end_date = self.start_date + timedelta(days=duration_days) 