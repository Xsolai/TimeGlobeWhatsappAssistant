from sqlalchemy import create_engine
from ..core.config import settings
from ..models.base import Base, metadata
# Import explicitly to ensure all models are registered
from ..models.all_models import (
    Business, 
    WABAStatus,
    BusinessSubscription,
    SubscriptionPlan,



    BookingDetail,
    BookModel,
    CustomerModel
)

def init_db():
    engine = create_engine(settings.DATABASE_URL)
    # This will create all tables defined in all imported models
    metadata.create_all(bind=engine)
    # print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 