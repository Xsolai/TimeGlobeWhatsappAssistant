import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

class Settings:
    # Project Info
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "TimeGlobe APPOINTMENT AI")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DESCRIPTION: str = os.getenv("DESCRIPTION", "TimeGlobe Appointment AI")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:3000")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/timeglobewhatsappassistant.db")
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("account_sid", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("auth_token", "")
    TWILIO_FROM_NUMBER: str = os.getenv("from_whatsapp_number", "")
    TWILIO_API_URL: str = os.getenv("TWILIO_API_URL", "https://messaging.twilio.com/v2/Channels/Senders")
    TWILIO_MESSAGING_SERVICE_SID: str = os.getenv("TWILIO_MESSAGING_SERVICE_SID", "")
    
    # Dialog360 Configuration
    DIALOG360_API_KEY: str = os.getenv("DIALOG360_API_KEY", "")
    DIALOG360_API_URL: str = os.getenv("DIALOG360_API_URL", "https://waba-v2.360dialog.io")
    DIALOG360_PHONE_NUMBER: str = os.getenv("DIALOG360_PHONE_NUMBER", "")
    
    # TimeGlobe Configuration
    TIME_GLOBE_BASE_URL: str = os.getenv("TIME_GLOBE_BASE_URL", "")
    TIME_GLOBE_LOGIN_USERNAME: str = os.getenv("TIME_GLOBE_LOGIN_USERNAME", "")
    TIME_GLOBE_LOGIN_PASSWORD: str = os.getenv("TIME_GLOBE_LOGIN_PASSWORD", "")
    TIME_GLOBE_API_KEY: str = os.getenv("TIME_GLOBE_API_KEY", "")
    WABA_ID: str = os.getenv("WABA_ID", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ASSISTANT_ID: str = os.getenv("OPENAI_ASSISTANT_ID", "")
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("SECRETE_KEY", "super-secret")
    ACCESS_TOKEN_EXPIRE_TIME: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_TIME", "30"))
    
    # Email Configuration
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
    EMAIL_USE_SSL: bool = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"

# Create a global settings instance
settings = Settings()
