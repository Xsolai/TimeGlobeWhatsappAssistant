import os
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def load_env() -> Dict[str, str]:
    """
    Load environment variables from .env file.
    Returns a dictionary of environment variables.
    """
    env_vars = {}
    
    try:
        # Try to load from .env file
        with open('.env', 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                    else:
                        logger.warning(f"Invalid line {line_num} in .env file: {line}")
                    
        logger.info("Environment variables loaded from .env file")
        
    except FileNotFoundError:
        logger.warning(".env file not found, using system environment variables")
        
    except Exception as e:
        logger.error(f"Error loading .env file: {str(e)}")
        
    # Override with system environment variables
    for key, value in os.environ.items():
        env_vars[key] = value
        
    # Log important WhatsApp Business API settings
    whatsapp_settings = {
        'WHATSAPP_APP_ID': env_vars.get('WHATSAPP_APP_ID', ''),
        'WHATSAPP_APP_SECRET': env_vars.get('WHATSAPP_APP_SECRET', ''),
        'WHATSAPP_WEBHOOK_VERIFY_TOKEN': env_vars.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN', ''),
    }
    
    for key, value in whatsapp_settings.items():
        if value:
            masked_value = value[:5] + '...' if len(value) > 5 else value
            logger.info(f"{key} loaded: {masked_value}")
        else:
            logger.warning(f"{key} not found in environment variables")
            
    return env_vars 