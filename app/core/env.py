import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

def load_env():
    """
    Load environment variables from .env file.
    Looks for .env file in the project root directory.
    """
    # Get the project root directory (2 levels up from this file)
    project_root = Path(__file__).resolve().parent.parent.parent
    env_path = project_root / '.env'
    
    logger.info(f"Looking for .env file at: {env_path}")
    
    if not env_path.exists():
        logger.error(f".env file not found at {env_path}")
        return os.environ
    
    logger.info(f".env file found at {env_path}")
    
    # Load the .env file
    load_dotenv(dotenv_path=str(env_path))

    
    # Log critical environment variables (without values for security)
    critical_vars = [
        "DIALOG360_API_KEY",
        "OPENAI_API_KEY",
        "DIALOG360_PHONE_NUMBER",
        "TIME_GLOBE_BASE_URL",
        "TIME_GLOBE_LOGIN_USERNAME",
        "TIME_GLOBE_LOGIN_PASSWORD",
        "TIME_GLOBE_API_KEY",
        "WABA_ID",
        "PARTNER_API_KEY",
        "PARTNER_ID"
    ]
    
    for var in critical_vars:
        if var in os.environ:
            logger.info(f"✓ {var} is set")
        else:
            logger.error(f"✗ {var} is not set")
    
    return os.environ 