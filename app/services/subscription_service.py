import logging
from sqlalchemy.orm import Session
from ..repositories.subscription_repository import SubscriptionPlanRepository
from ..schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate
from fastapi import HTTPException

# Set up logger
logger = logging.getLogger("app.subscription_service")


class SubscriptionPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = SubscriptionPlanRepository(db)

    def create_plan(self, plan_data: SubscriptionPlanCreate):
        """Business logic for creating a subscription plan"""
        try:
            logger.info("Creating a new subscription plan: %s", plan_data)
            plan = self.plan_repo.create_plan(plan_data)
            logger.info("Subscription plan created successfully with ID: %d", plan.id)
            return plan
        except Exception as e:
            logger.error("Error creating subscription plan: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Failed to create subscription plan"
            )

    def get_plan_by_id(self, plan_id: int):
        """Fetch a subscription plan by ID"""
        try:
            logger.info("Fetching subscription plan with ID: %d", plan_id)
            plan = self.plan_repo.get_plan_by_id(plan_id)
            if not plan:
                logger.warning("Subscription plan not found for ID: %d", plan_id)
                raise HTTPException(
                    status_code=404, detail="Subscription plan not found"
                )
            return plan
        except Exception as e:
            logger.error("Error fetching subscription plan: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Failed to fetch subscription plan"
            )

    def get_all_plans(self):
        """Fetch all active subscription plans"""
        try:
            logger.info("Fetching all active subscription plans")
            return self.plan_repo.get_all_plans()
        except Exception as e:
            logger.error("Error fetching subscription plans: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Failed to fetch subscription plans"
            )

    def update_plan(self, plan_id: int, plan_data: SubscriptionPlanUpdate):
        """Update an existing subscription plan"""
        try:
            logger.info("Updating subscription plan ID: %d", plan_id)
            updated_plan = self.plan_repo.update_plan(plan_id, plan_data)
            if not updated_plan:
                logger.warning("Failed to update subscription plan ID: %d", plan_id)
                raise HTTPException(
                    status_code=404, detail="Subscription plan not found"
                )
            logger.info("Subscription plan ID %d updated successfully", plan_id)
            return updated_plan
        except Exception as e:
            logger.error("Error updating subscription plan: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Failed to update subscription plan"
            )

    def delete_plan(self, plan_id: int):
        """Delete a subscription plan"""
        try:
            logger.info("Deleting subscription plan ID: %d", plan_id)
            deleted = self.plan_repo.delete_plan(plan_id)
            if not deleted:
                logger.warning(
                    "Subscription plan not found for deletion: ID %d", plan_id
                )
                raise HTTPException(
                    status_code=404, detail="Subscription plan not found"
                )
            logger.info("Subscription plan ID %d deleted successfully", plan_id)
            return {"message": "Subscription plan deleted successfully"}
        except Exception as e:
            logger.error("Error deleting subscription plan: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Failed to delete subscription plan"
            )

    def subscribe_user(self, user_id: int, subscription_id: int):
        """Subscribe a user"""
        try:
            logger.info(
                "Subscribing user ID %d to subscription ID %d", user_id, subscription_id
            )
            subscriber = self.plan_repo.subscribe_user(user_id, subscription_id)
            if not subscriber:
                logger.warning("Subscription failed for user ID %d", user_id)
                raise HTTPException(
                    status_code=500, detail="Error processing subscription request"
                )
            logger.info("User ID %d subscribed successfully", user_id)
            return {"message": "Subscription successful", "subscription": subscriber}
        except Exception as e:
            logger.error("Error subscribing user: %s", str(e))
            raise HTTPException(status_code=500, detail="Failed to subscribe user")

    def get_user_subscriptions(self, user_id: int):
        """Fetch active subscriptions for a user"""
        try:
            logger.info("Fetching subscriptions for user ID: %d", user_id)
            return self.plan_repo.get_user_subscriptions(user_id)
        except Exception as e:
            logger.error("Error fetching user subscriptions: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Failed to fetch user subscriptions"
            )

    def cancel_subscription(self, user_id: int, subscription_id: int):
        """Cancel a user's subscription"""
        try:
            logger.info(
                "Cancelling subscription ID %d for user ID %d", subscription_id, user_id
            )
            subscription = self.plan_repo.cancel_subscription(user_id, subscription_id)
            if not subscription:
                logger.warning(
                    "Failed to cancel subscription ID %d for user ID %d",
                    subscription_id,
                    user_id,
                )
                raise HTTPException(
                    status_code=500, detail="Error processing cancellation request"
                )
            logger.info(
                "Subscription ID %d canceled successfully for user ID %d",
                subscription_id,
                user_id,
            )
            return {"message": "Subscription canceled successfully"}
        except Exception as e:
            logger.error("Error canceling subscription: %s", str(e))
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
