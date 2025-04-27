import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """
    Load environment variables from .env file.
    Looks for .env file in the project root directory.
    """
    # Get the project root directory (2 levels up from this file)
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Look for .env file in project root
    env_path = project_root / '.env'
    
    # Load the .env file
    load_dotenv(dotenv_path=str(env_path))
    
    return os.environ 