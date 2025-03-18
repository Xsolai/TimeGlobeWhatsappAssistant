from sqlalchemy.orm import Session
from ..models.subscription_plan import SubscriptionPlan
from ..schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate


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
