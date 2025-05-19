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

    # Partner API Settings
    PARTNER_API_KEY: str = env.get("PARTNER_API_KEY", "")
    PARTNER_ID: str = env.get("PARTNER_ID", "")

    # Dialog360 Settings
    DIALOG360_API_KEY: str = env.get("DIALOG360_API_KEY", "")
    DIALOG360_API_URL: str = env.get("DIALOG360_API_URL", "https://waba-v2.360dialog.io")
    DIALOG360_PHONE_NUMBER: str = env.get("DIALOG360_PHONE_NUMBER", "")

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
    DESCRIPTION: str = env.get("DESCRIPTION", "TimeGlobe WhatsApp Assistant API powered by 360dialog")
    ALLOWED_ORIGINS: str = env.get("ALLOWED_ORIGINS", "*")
    
    # Additional fields from your .env file
    from_whatsapp_number: str = env.get("from_whatsapp_number", "")
    account_sid: str = env.get("account_sid", "")
    auth_token: str = env.get("auth_token", "")
    SECRETE_KEY: str = env.get("SECRETE_KEY", "")
    API_BASE_URL: str = env.get("API_BASE_URL", "")
    EMAIL_SENDER: str = env.get("EMAIL_SENDER", "")

    FRONTEND_RESET_PASSWORD_URL: str = "http://localhost:3000/reset-password"

    # This is the important part - allows extra fields
    model_config = {
        "extra": "ignore"  # Allows extra fields from env file that aren't defined in the class
    }

# Create settings instance
settings = Settings()

# Log important settings to verify they're loaded correctly
logger.info(f"DIALOG360_API_KEY loaded: {bool(settings.DIALOG360_API_KEY)}")
logger.info(f"DIALOG360_API_URL: {settings.DIALOG360_API_URL}")
