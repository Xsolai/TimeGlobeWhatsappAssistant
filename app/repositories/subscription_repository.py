from sqlalchemy.orm import Session
from ..models.subscription_plan import SubscriptionPlan
from ..models.user_subscription import UserSubscription
from ..schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate
from datetime import datetime, timezone


class SubscriptionPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(self, plan_data: SubscriptionPlanCreate) -> SubscriptionPlan:
        """Creates a new subscription plan"""
        new_plan = SubscriptionPlan(**plan_data.model_dump())
        self.db.add(new_plan)
        self.db.commit()
        self.db.refresh(new_plan)
        return new_plan

    def subscribe_user(self, user_id: int, subscription_id: int) -> UserSubscription:
        """Subscribe a user to a subscription plan"""
        subscription_plan = (
            self.db.query(SubscriptionPlan).filter_by(id=subscription_id).first()
        )
        if not subscription_plan:
            return None  # Subscription plan doesn't exist

        new_subscription = UserSubscription(
            user_id=user_id,
            subscription_id=subscription_id,
            start_date=datetime.now(timezone.utc),
        )
        new_subscription.activate_subscription(subscription_plan.duration_in_days)

        self.db.add(new_subscription)
        self.db.commit()
        self.db.refresh(new_subscription)
        return new_subscription

    def get_user_subscriptions(self, user_id: int):
        """Get all active subscriptions of a user"""
        return (
            self.db.query(UserSubscription)
            .filter(
                UserSubscription.user_id == user_id, UserSubscription.is_active == True
            )
            .all()
        )

    def cancel_subscription(self, user_id: int, subscription_id: int) -> bool:
        """Cancel an active subscription"""
        subscription = (
            self.db.query(UserSubscription)
            .filter(
                UserSubscription.user_id == user_id,
                UserSubscription.subscription_id == subscription_id,
            )
            .first()
        )
        if not subscription:
            return False

        self.db.delete(subscription)
        self.db.commit()
        return True

    def get_plan_by_id(self, plan_id: int) -> SubscriptionPlan:
        """Retrieves a subscription plan by ID"""
        return (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.id == plan_id)
            .first()
        )

    def get_all_plans(self):
        """Retrieves all active subscription plans"""
        return (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.is_active == True)
            .all()
        )

    def update_plan(
        self, plan_id: int, plan_data: SubscriptionPlanUpdate
    ) -> SubscriptionPlan:
        """Updates a subscription plan"""
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            return None

        for key, value in plan_data.model_dump(exclude_unset=True).items():
            setattr(plan, key, value)

        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete_plan(self, plan_id: int) -> bool:
        """Deletes a subscription plan"""
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            return False

        self.db.delete(plan)
        self.db.commit()
        return True
