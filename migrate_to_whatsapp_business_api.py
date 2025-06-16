#!/usr/bin/env python3
"""
Database migration script for transitioning from Dialog360 to WhatsApp Business API.
This script helps update existing business records with new WhatsApp Business API credentials.
"""

import os
import sys
import logging
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import SessionLocal
from app.models.business_model import Business, WABAStatus
from app.core.env import load_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def migrate_business_records():
    """
    Migrate business records from Dialog360 to WhatsApp Business API format.
    """
    logger.info("🚀 Starting WhatsApp Business API migration")
    logger.info("=" * 60)
    
    # Load environment variables
    load_env()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all businesses that need migration
        businesses = db.query(Business).all()
        
        if not businesses:
            logger.info("📭 No business records found in database")
            return
        
        logger.info(f"📊 Found {len(businesses)} business records to check")
        
        migrated_count = 0
        skipped_count = 0
        
        for business in businesses:
            logger.info(f"\n🏢 Processing business: {business.business_name} ({business.email})")
            
            # Check if business needs migration
            if needs_migration(business):
                if migrate_single_business(business, db):
                    migrated_count += 1
                    logger.info(f"✅ Successfully migrated: {business.business_name}")
                else:
                    logger.error(f"❌ Failed to migrate: {business.business_name}")
            else:
                skipped_count += 1
                logger.info(f"⏭️ Skipped (already migrated): {business.business_name}")
        
        # Commit all changes
        db.commit()
        
        logger.info(f"\n📊 Migration Summary:")
        logger.info(f"✅ Migrated: {migrated_count}")
        logger.info(f"⏭️ Skipped: {skipped_count}")
        logger.info(f"📱 Total processed: {len(businesses)}")
        
        if migrated_count > 0:
            logger.info(f"\n🎉 Migration completed successfully!")
            logger.info(f"Please update your environment variables and test the integration.")
        
    except Exception as e:
        logger.error(f"💥 Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def needs_migration(business: Business) -> bool:
    """
    Check if a business record needs migration to WhatsApp Business API.
    """
    # Check if it's still using Dialog360 format
    if business.api_key and business.api_key.startswith(('JGt', 'AT')):  # Common Dialog360 key prefixes
        return True
    
    # Check if it has Dialog360-style endpoint
    if business.api_endpoint and 'waba-v2.360dialog.io' in business.api_endpoint:
        return True
    
    # Check if it lacks WhatsApp Business API fields
    if not business.app_id and business.api_key:
        return True
    
    return False

def migrate_single_business(business: Business, db) -> bool:
    """
    Migrate a single business record to WhatsApp Business API format.
    """
    try:
        # Interactive migration - ask for new credentials
        print(f"\n📝 Migrating business: {business.business_name}")
        print(f"   📧 Email: {business.email}")
        print(f"   📱 WhatsApp Number: {business.whatsapp_number}")
        print(f"   🆔 Current API Key: {business.api_key[:10]}..." if business.api_key else "   🆔 No API Key")
        
        # Get new credentials from user or environment
        new_credentials = get_new_credentials(business)
        
        if not new_credentials:
            logger.warning(f"⚠️ No new credentials provided for {business.business_name}")
            return False
        
        # Backup old values
        backup_data = {
            'old_api_key': business.api_key,
            'old_api_endpoint': business.api_endpoint,
            'old_channel_id': business.channel_id,
            'migration_date': datetime.now()
        }
        
        # Update with new WhatsApp Business API credentials
        business.api_key = new_credentials['access_token']
        business.channel_id = new_credentials['phone_number_id']
        business.app_id = new_credentials['app_id']
        business.api_endpoint = None  # Not needed for WhatsApp Business API
        business.waba_status = WABAStatus.connected
        
        # Store backup data in a JSON field if available
        if hasattr(business, 'migration_backup'):
            business.migration_backup = backup_data
        
        logger.info(f"📝 Updated credentials for {business.business_name}")
        return True
        
    except Exception as e:
        logger.error(f"💥 Failed to migrate {business.business_name}: {str(e)}")
        return False

def get_new_credentials(business: Business) -> dict:
    """
    Get new WhatsApp Business API credentials for a business.
    """
    # Check if credentials are provided via environment variables
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    app_id = os.getenv("WHATSAPP_APP_ID")
    
    if all([access_token, phone_number_id, app_id]):
        logger.info("📋 Using credentials from environment variables")
        return {
            'access_token': access_token,
            'phone_number_id': phone_number_id,
            'app_id': app_id
        }
    
    # Interactive mode - ask user for credentials
    print(f"\n🔑 Enter WhatsApp Business API credentials for {business.business_name}:")
    
    try:
        access_token = input("   📱 WhatsApp Access Token: ").strip()
        if not access_token:
            return None
            
        phone_number_id = input("   📞 Phone Number ID: ").strip()
        if not phone_number_id:
            return None
            
        app_id = input("   🆔 Facebook App ID: ").strip()
        if not app_id:
            return None
        
        return {
            'access_token': access_token,
            'phone_number_id': phone_number_id,
            'app_id': app_id
        }
        
    except KeyboardInterrupt:
        print("\n⏸️ Migration cancelled by user")
        return None

if __name__ == "__main__":
    print("🔄 WhatsApp Business API Migration Tool")
    print("=" * 50)
    migrate_business_records() 