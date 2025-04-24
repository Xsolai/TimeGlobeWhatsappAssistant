#!/usr/bin/env python
"""
Standalone script to verify and create all database tables.
Run this script with: python app/db_setup.py
"""
import os
import sys
import logging
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings
from app.models.base import Base
from app.models.all_models import (
    Business, 
    WABAStatus,
    BusinessSubscription,
    SubscriptionPlan,
    SenderModel,
    ThreadModel,
    ActiveRunModel,
    BookingDetail,
    BookModel,
    CustomerModel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_setup")

def setup_database():
    """Verify and create all database tables."""
    logger.info(f"Using database: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        sys.exit(1)
    
    # Get all defined models
    model_tables = set(Base.metadata.tables.keys())
    logger.info(f"Models defined ({len(model_tables)}): {', '.join(model_tables)}")
    
    # Check existing tables
    try:
        inspector = inspect(engine)
        db_tables = set(inspector.get_table_names())
        logger.info(f"Existing tables ({len(db_tables)}): {', '.join(db_tables)}")
        
        # Find missing tables
        missing_tables = model_tables - db_tables
        if missing_tables:
            logger.info(f"Missing tables ({len(missing_tables)}): {', '.join(missing_tables)}")
        else:
            logger.info("All tables already exist in the database")
    except Exception as e:
        logger.error(f"Failed to inspect database: {str(e)}")
        missing_tables = model_tables  # Assume all tables need to be created
    
    # Create tables
    try:
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        sys.exit(1)
    
    # Verify tables after creation
    try:
        inspector = inspect(engine)
        final_tables = set(inspector.get_table_names())
        logger.info(f"Final table count: {len(final_tables)}")
        
        # Check if any tables are still missing
        still_missing = model_tables - final_tables
        if still_missing:
            logger.warning(f"Tables still missing: {', '.join(still_missing)}")
        else:
            logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Failed to verify tables: {str(e)}")
    
    return True

if __name__ == "__main__":
    logger.info("Starting database setup...")
    setup_database()
    logger.info("Database setup complete") 