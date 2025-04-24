"""
Database setup module to be imported during application startup.
This ensures all models are loaded and tables are created.
"""
from sqlalchemy import create_engine, inspect
from ..core.config import settings
from ..models.base import Base
# Import all models explicitly to register them with SQLAlchemy
from ..models.all_models import (
    Business, 
    WABAStatus,
    BusinessSubscription,
    SubscriptionPlan,
    WASenderModel,
    ThreadModel,
    ActiveRunModel,
    BookingDetail,
    BookModel,
    CustomerModel
)
import logging

logger = logging.getLogger(__name__)

def setup_database():
    """
    Ensure all tables are created in the database.
    This function should be called during application startup.
    """
    engine = create_engine(settings.DATABASE_URL)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Verify all tables were created
    inspector = inspect(engine)
    db_tables = inspector.get_table_names()
    model_tables = set(Base.metadata.tables.keys())
    
    # Log table information
    logger.info(f"Database setup complete. Found {len(db_tables)} tables.")
    
    # Verify all expected tables exist
    missing_tables = model_tables - set(db_tables)
    if missing_tables:
        logger.warning(f"Some tables are missing: {', '.join(missing_tables)}")
    else:
        logger.info("All expected tables exist in the database.")
    
    return True 