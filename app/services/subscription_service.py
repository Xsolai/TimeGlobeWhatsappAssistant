from sqlalchemy.orm import Session
from ..repositories.subscription_repository import SubscriptionPlanRepository
from ..schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate


class SubscriptionPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = SubscriptionPlanRepository(db)

    def create_plan(self, plan_data: SubscriptionPlanCreate):
        """Business logic for creating a subscription plan"""
        return self.plan_repo.create_plan(plan_data)

    def get_plan_by_id(self, plan_id: int):
        """Fetch a subscription plan by ID"""
        return self.plan_repo.get_plan_by_id(plan_id)

    def get_all_plans(self):
        """Fetch all active subscription plans"""
        return self.plan_repo.get_all_plans()

    def update_plan(self, plan_id: int, plan_data: SubscriptionPlanUpdate):
        """Update an existing subscription plan"""
        return self.plan_repo.update_plan(plan_id, plan_data)

    def delete_plan(self, plan_id: int):
        """Delete a subscription plan"""
        return self.plan_repo.delete_plan(plan_id)
