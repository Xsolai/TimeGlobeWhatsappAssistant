from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from .base import Base


class UserSubscription(Base):
    __tablename__ = "UserSubscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    subscription_id = Column(
        Integer, ForeignKey("SubscriptionPlans.id"), nullable=False
    )
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships (assuming User and SubscriptionPlan models exist)
    user = relationship("UserModel", back_populates="subscriptions")
    subscription = relationship("SubscriptionPlan", back_populates="users")

    def activate_subscription(self, duration_days: int):
        """Sets the end date based on subscription duration"""
        self.end_date = self.start_date + timedelta(days=duration_days)
