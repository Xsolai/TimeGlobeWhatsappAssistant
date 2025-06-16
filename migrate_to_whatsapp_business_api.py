#!/usr/bin/env python3
"""
Database migration script for transitioning to WhatsApp Business API.
This script updates business records to use the new WhatsApp Business API format.
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.business_model import Business
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_session():
    """Create a database session."""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def migrate_business_records():
    """Migrate business records to WhatsApp Business API format."""
    session = get_db_session()
    try:
        # Get all business records
        businesses = session.query(Business).all()
        logger.info(f"Found {len(businesses)} business records to migrate")
        
        for business in businesses:
            try:
                # Generate new IDs for subscription-related records
                subscription_plan_id = str(uuid.uuid4())
                business_subscription_id = str(uuid.uuid4())
                
                # Update business record with WhatsApp Business API settings
                business.api_key = settings.WHATSAPP_ACCESS_TOKEN or ""
                business.channel_id = settings.WHATSAPP_PHONE_NUMBER_ID or ""
                business.webhook_url = f"{settings.API_BASE_URL}/api/whatsapp/webhook" if settings.API_BASE_URL else ""
                business.app_id = settings.WHATSAPP_APP_ID or ""
                business.waba_status = "connected"  # Update status to connected
                
                logger.info(f"Updated business record for {business.business_name}")
                
            except Exception as e:
                logger.error(f"Error updating business {business.business_name}: {str(e)}")
                continue
        
        # Commit changes
        session.commit()
        logger.info("Successfully migrated all business records")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    try:
        logger.info("Starting WhatsApp Business API migration")
        
        # Log current settings
        logger.info("Current WhatsApp Business API settings:")
        logger.info(f"WHATSAPP_APP_ID: {settings.WHATSAPP_APP_ID}")
        logger.info(f"WHATSAPP_CONFIGURATION_ID: {settings.WHATSAPP_CONFIGURATION_ID}")
        logger.info(f"WHATSAPP_ACCESS_TOKEN: {'Set' if settings.WHATSAPP_ACCESS_TOKEN else 'Not set'}")
        logger.info(f"WHATSAPP_PHONE_NUMBER_ID: {'Set' if settings.WHATSAPP_PHONE_NUMBER_ID else 'Not set'}")
        logger.info(f"API_BASE_URL: {settings.API_BASE_URL}")
        
        migrate_business_records()
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1) 