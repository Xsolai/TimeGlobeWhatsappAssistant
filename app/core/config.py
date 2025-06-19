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
    WHATSAPP_APP_SECRET: str = env.get("WHATSAPP_APP_SECRET", "12cd8f4a89c6eb0fe266f4bb8ca3e2e4")
    WHATSAPP_CONFIGURATION_ID: str = "966700112247031"
    WHATSAPP_ACCESS_TOKEN: str = env.get("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_SYSTEM_TOKEN: str = env.get("WHATSAPP_SYSTEM_TOKEN", "EAASK1LvnU7oBOzN1ZBcOXDPOJ7pVpypZBerrBz4kIyZAFvnT4JOUAUeMPy6vq9B1Mg54msZBJHicgl44d2COkCbVNtDKaMAx2zto4yqp0rw3re9DiRz3ISUsLbXKJCNutcJ3YWqaZCB0isBM2oy7bSPMegVqZBrVTav4lZBkrDrV1iUSyWM8UxNyTKbj1KQqnqOyAZDZD")
    # IMPORTANT: This must match the Valid OAuth Redirect URI in your Facebook App settings
    WHATSAPP_OAUTH_REDIRECT_URI: str = env.get("WHATSAPP_OAUTH_REDIRECT_URI", "https://9b9f-2a09-bac5-503c-18be-00-277-5.ngrok-free.app/api/whatsapp/oauth/callback")
    WHATSAPP_PHONE_NUMBER_ID: str = env.get("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = env.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = env.get("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_API_VERSION: str = env.get("WHATSAPP_API_VERSION", "v18.0")

    # TimeGlobe Settings
    TIMEGLOBE_BASE_URL: str = env.get("TIMEGLOBE_BASE_URL", "https://online.time-globe-crs.de/")
    TIMEGLOBE_LOGIN_USERNAME: str = env.get("TIMEGLOBE_LOGIN_USERNAME", "termin@timeglobe.de")
    TIMEGLOBE_LOGIN_PASSWORD: str = env.get("TIMEGLOBE_LOGIN_PASSWORD", "123")
    TIMEGLOBE_API_KEY: str = env.get("TIMEGLOBE_API_KEY", "96f1f820d19b7d5fe3de0d6a3aefcb2848109d507a3ddf0f95fcda285cff2b33")
    WABA_ID: str = env.get("WABA_ID", "")

    # OpenAI Settings
    OPENAI_API_KEY: str = env.get("OPENAI_API_KEY", "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")

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
    EMAIL_USERNAME: str = env.get("EMAIL_USERNAME", "abdullahmustafa2435@gmail.com")
    EMAIL_PASSWORD: str = env.get("EMAIL_PASSWORD", "iazi iycs jjjg epeg")
    EMAIL_FROM: str = env.get("EMAIL_FROM", "abdullahmustafa2435@gmail.com")
    EMAIL_USE_TLS: bool = env.get("EMAIL_USE_TLS", "True") == "True"
    EMAIL_USE_SSL: bool = env.get("EMAIL_USE_SSL", "False") == "True"

    # App metadata
    PROJECT_NAME: str = env.get("PROJECT_NAME", "TimeGlobe APPOINTMENT AI")
    VERSION: str = env.get("VERSION", "1.0.0")
    DESCRIPTION: str = env.get("DESCRIPTION", "TimeGlobe Appointment AI")
    ALLOWED_ORIGINS: str = env.get("ALLOWED_ORIGINS", "*")
    
    # Additional fields from your .env file
    from_whatsapp_number: str = env.get("from_whatsapp_number", "")
    SECRETE_KEY: str = env.get("SECRETE_KEY", "JGtbI8U82BUBL6SYldQNMd6SAK")
    API_BASE_URL: str = env.get("API_BASE_URL", "https://9b9f-2a09-bac5-503c-18be-00-277-5.ngrok-free.app")
    EMAIL_SENDER: str = env.get("EMAIL_SENDER", "abdullahmustafa2435@gmail.com")
    
    # Partner API Settings
    PARTNER_API_KEY: str = env.get("PARTNER_API_KEY", "794c76fd-7b5c-49a2-ae32-e123fabcac74")
    PARTNER_ID: str = env.get("PARTNER_ID", "MalHtRPA")

    FRONTEND_RESET_PASSWORD_URL: str = "https://timeglobe.ecomtask.de/reset-password"

    # This is the important part - allows extra fields
    model_config = {
        "extra": "ignore"  # Allows extra fields from env file that aren't defined in the class
    }

# Create settings instance
settings = Settings()

# Log important settings to verify they're loaded correctly
logger.info(f"WHATSAPP_APP_ID: {settings.WHATSAPP_APP_ID}")
logger.info(f"WHATSAPP_APP_SECRET loaded: {bool(settings.WHATSAPP_APP_SECRET)}")
logger.info(f"WHATSAPP_CONFIGURATION_ID: {settings.WHATSAPP_CONFIGURATION_ID}")
logger.info(f"WHATSAPP_ACCESS_TOKEN loaded: {bool(settings.WHATSAPP_ACCESS_TOKEN)}")
logger.info(f"WHATSAPP_SYSTEM_TOKEN loaded: {bool(settings.WHATSAPP_SYSTEM_TOKEN)}")
logger.info(f"WHATSAPP_PHONE_NUMBER_ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
logger.info(f"WHATSAPP_WEBHOOK_VERIFY_TOKEN loaded: {bool(settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN)}")
logger.info(f"WHATSAPP_BUSINESS_ACCOUNT_ID: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
