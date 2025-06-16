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
    DATABASE_URL: str = env.get(
        "DATABASE_URL", "sqlite:///./timeglobewhatsappassistant.db"
    )

    # WhatsApp Business API Settings
    WHATSAPP_APP_ID: str = "1278546197042106"
    WHATSAPP_CONFIGURATION_ID: str = "966700112247031"
    WHATSAPP_ACCESS_TOKEN: str = env.get("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = env.get("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = env.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = env.get("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_APP_SECRET: str = env.get("WHATSAPP_APP_SECRET", "")
    WHATSAPP_API_VERSION: str = env.get("WHATSAPP_API_VERSION", "v18.0")

    # TimeGlobe Settings
    TIMEGLOBE_BASE_URL: str = env.get("TIMEGLOBE_BASE_URL", "")
    TIMEGLOBE_LOGIN_USERNAME: str = env.get("TIMEGLOBE_LOGIN_USERNAME", "")
    TIMEGLOBE_LOGIN_PASSWORD: str = env.get("TIMEGLOBE_LOGIN_PASSWORD", "")
    TIMEGLOBE_API_KEY: str = env.get("TIMEGLOBE_API_KEY", "")
    WABA_ID: str = env.get("WABA_ID", "")

    # OpenAI Settings
    OPENAI_API_KEY: str = env.get("OPENAI_API_KEY", "")

    # JWT Settings
    JWT_SECRET_KEY: str = env.get("JWT_SECRET_KEY", "super-secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN_MINUTES: int = 60 * 24 * 7  # 7 days
    ACCESS_TOKEN_EXPIRE_TIME: int = int(env.get("ACCESS_TOKEN_EXPIRE_TIME", "30"))

    # External APIs
    OPEN_WEATHER_API_KEY: str = env.get("OPEN_WEATHER_API_KEY", "")
    
    # Email Settings
    EMAIL_HOST: str = env.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(env.get("EMAIL_PORT", "587"))
    EMAIL_USERNAME: str = env.get("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = env.get("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = env.get("EMAIL_FROM", "")
    EMAIL_USE_TLS: bool = env.get("EMAIL_USE_TLS", "True") == "True"
    EMAIL_USE_SSL: bool = env.get("EMAIL_USE_SSL", "False") == "True"

    # App metadata
    PROJECT_NAME: str = env.get("PROJECT_NAME", "TimeGlobe WhatsApp Assistant API")
    VERSION: str = env.get("VERSION", "1.0.0")
    DESCRIPTION: str = env.get("DESCRIPTION", "TimeGlobe WhatsApp Assistant API powered by Meta WhatsApp Business API")
    ALLOWED_ORIGINS: str = env.get("ALLOWED_ORIGINS", "*")
    
    # Additional fields from your .env file
    from_whatsapp_number: str = env.get("from_whatsapp_number", "")
    SECRETE_KEY: str = env.get("SECRETE_KEY", "")
    API_BASE_URL: str = env.get("API_BASE_URL", "")
    EMAIL_SENDER: str = env.get("EMAIL_SENDER", "")

    FRONTEND_RESET_PASSWORD_URL: str = "https://timeglobe.ecomtask.de/reset-password"

    # This is the important part - allows extra fields
    model_config = {
        "extra": "ignore"  # Allows extra fields from env file that aren't defined in the class
    }

# Create settings instance
settings = Settings()

# Log important settings to verify they're loaded correctly
logger.info(f"WHATSAPP_APP_ID: {settings.WHATSAPP_APP_ID}")
logger.info(f"WHATSAPP_CONFIGURATION_ID: {settings.WHATSAPP_CONFIGURATION_ID}")
logger.info(f"WHATSAPP_ACCESS_TOKEN loaded: {bool(settings.WHATSAPP_ACCESS_TOKEN)}")
logger.info(f"WHATSAPP_PHONE_NUMBER_ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
logger.info(f"WHATSAPP_WEBHOOK_VERIFY_TOKEN loaded: {bool(settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN)}")
logger.info(f"WHATSAPP_BUSINESS_ACCOUNT_ID: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
