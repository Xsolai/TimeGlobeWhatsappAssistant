from pydantic_settings import BaseSettings
from .env import load_env
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables at module level
env = load_env()

class Settings(BaseSettings):
    app_name: str = "TimeGlobeWhatsappAssistant"
    ENVIRONMENT: str = env.get("ENVIRONMENT", "development")
    DATABASE_URL: str = env.get("DATABASE_URL", "sqlite:///./timeglobewhatsappassistant.db")

    # WhatsApp Business API Settings
    WHATSAPP_APP_ID: str = env.get("WHATSAPP_APP_ID", "")
    WHATSAPP_APP_SECRET: str = env.get("WHATSAPP_APP_SECRET", "")
    WHATSAPP_SYSTEM_TOKEN: str = env.get("WHATSAPP_SYSTEM_TOKEN", "")
    WHATSAPP_OAUTH_REDIRECT_URI: str = env.get("WHATSAPP_OAUTH_REDIRECT_URI", "")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = env.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
    WHATSAPP_API_VERSION: str = env.get("WHATSAPP_API_VERSION", "v18.0")

    # TimeGlobe Settings
    TIMEGLOBE_BASE_URL: str = env.get("TIMEGLOBE_BASE_URL", "https://timeglobe.app/api")
    TIMEGLOBE_LOGIN_USERNAME: str = env.get("TIMEGLOBE_LOGIN_USERNAME", "")
    TIMEGLOBE_LOGIN_PASSWORD: str = env.get("TIMEGLOBE_LOGIN_PASSWORD", "")
    TIMEGLOBE_API_KEY: str = env.get("TIMEGLOBE_API_KEY", "")

    # OpenAI Settings
    OPENAI_API_KEY: str = env.get("OPENAI_API_KEY", "")

    # JWT Settings
    JWT_SECRET_KEY: str = env.get("JWT_SECRET_KEY", "super-secret")
    JWT_EXPIRES_IN_MINUTES: int = 60 * 24 * 7  # 7 days
    ACCESS_TOKEN_EXPIRE_TIME: int = int(env.get("ACCESS_TOKEN_EXPIRE_TIME", "30"))

    # App metadata
    PROJECT_NAME: str = env.get("PROJECT_NAME", "TimeGlobe APPOINTMENT AI")
    VERSION: str = env.get("VERSION", "1.0.0")
    ALLOWED_ORIGINS: str = env.get("ALLOWED_ORIGINS", "*")
    
    # API Configuration
    API_BASE_URL: str = env.get("API_BASE_URL", "")

    # Frontend URLs
    FRONTEND_RESET_PASSWORD_URL: str = env.get("FRONTEND_RESET_PASSWORD_URL", "https://timeglobe.ecomtask.de/reset-password")

    # This is the important part - allows extra fields
    model_config = {
        "extra": "ignore"  # Allows extra fields from env file that aren't defined in the class
    }

# Create settings instance
settings = Settings()

# Log important settings to verify they're loaded correctly (without exposing sensitive values)
logger.info(f"WHATSAPP_APP_ID: {settings.WHATSAPP_APP_ID}")
logger.info(f"WHATSAPP_APP_SECRET loaded: {bool(settings.WHATSAPP_APP_SECRET)}")
logger.info(f"WHATSAPP_SYSTEM_TOKEN loaded: {bool(settings.WHATSAPP_SYSTEM_TOKEN)}")
logger.info(f"WHATSAPP_WEBHOOK_VERIFY_TOKEN loaded: {bool(settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN)}")
logger.info(f"TIMEGLOBE_BASE_URL: {settings.TIMEGLOBE_BASE_URL}")
logger.info(f"TIMEGLOBE_API_KEY loaded: {bool(settings.TIMEGLOBE_API_KEY)}")
logger.info(f"OPENAI_API_KEY loaded: {bool(settings.OPENAI_API_KEY)}")
logger.info(f"Environment: {settings.ENVIRONMENT}")
