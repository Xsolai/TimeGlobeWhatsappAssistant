import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

def load_env():
    """
    Load environment variables from .env file directly with a simplified approach.
    Returns a dictionary of environment variables.
    """
    # Get the absolute path to the .env file
    project_root = Path(__file__).resolve().parent.parent.parent
    env_path = project_root / '.env'
    
    logger.info(f"Looking for .env file at: {env_path}")
    
    # Dictionary to store environment variables
    env_vars = {}
    
    if not env_path.exists():
        logger.error(f".env file not found at {env_path}")
        return os.environ
    
    logger.info(f".env file found at {env_path}")
    
    # Load environment variables from .env file
    try:
        # First load with dotenv to populate os.environ
        load_dotenv(dotenv_path=str(env_path))
        
        # Then also manually parse the file to ensure we get everything
        with open(env_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Split line on first equals sign
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                        
                    # Store in our dictionary and ensure it's in os.environ too
                    env_vars[key] = value
                    os.environ[key] = value
                    logger.info(f"Loaded environment variable: {key}")
    except Exception as e:
        logger.error(f"Error loading .env file: {str(e)}")
    
    # Override Dialog360 API key specifically to ensure it works
    dialog360_key = env_vars.get('DIALOG360_API_KEY', '')
    if dialog360_key:
        # Remove quotes if present
        if dialog360_key.startswith('"') and dialog360_key.endswith('"'):
            dialog360_key = dialog360_key[1:-1]
        logger.info(f"Dialog360 API key loaded: {dialog360_key[:5]}...")
        os.environ['DIALOG360_API_KEY'] = dialog360_key
        env_vars['DIALOG360_API_KEY'] = dialog360_key
    else:
        logger.error("Dialog360 API key not found in .env file")
    
    # Return the combined environment
    return {**os.environ, **env_vars} 