from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    app_name: str = "TimeGlobeWhatsappAssistant"
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "sqlite:///./timeglobewhatsappassistant.db"
    )

    # Twilio Settings - keeping for backwards compatibility
    account_sid: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_whatsapp_number: str = os.environ.get("TWILIO_FROM_NUMBER", "")
    TWILIO_API_URL: str = os.environ.get("TWILIO_API_URL", "")
    TWILIO_MESSAGING_SERVICE_SID: str = os.environ.get("TWILIO_MESSAGING_SERVICE_SID", "")

    # Dialog360 Settings
    DIALOG360_API_KEY: str = os.environ.get("DIALOG360_API_KEY", "")
    DIALOG360_API_URL: str = os.environ.get("DIALOG360_API_URL", "https://waba.360dialog.io/v1")
    DIALOG360_PHONE_NUMBER: str = os.environ.get("DIALOG360_PHONE_NUMBER", "")

    # TimeGlobe Settings
    TIME_GLOBE_BASE_URL: str = os.environ.get("TIME_GLOBE_BASE_URL", "")
    TIME_GLOBE_LOGIN_USERNAME: str = os.environ.get("TIME_GLOBE_LOGIN_USERNAME", "")
    TIME_GLOBE_LOGIN_PASSWORD: str = os.environ.get("TIME_GLOBE_LOGIN_PASSWORD", "")
    TIME_GLOBE_API_KEY: str = os.environ.get("TIME_GLOBE_API_KEY", "")
    WABA_ID: str = os.environ.get("WABA_ID", "")

    # OpenAI Settings
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_ASSISTANT_ID: str = os.environ.get("OPENAI_ASSISTANT_ID", "")

    # JWT Settings
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "super-secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN_MINUTES: int = 60 * 24 * 7  # 7 days
    ACCESS_TOKEN_EXPIRE_TIME: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_TIME", "30"))

    # External APIs
    OPEN_WEATHER_API_KEY: str = os.environ.get("OPEN_WEATHER_API_KEY", "")
    
    # Email Settings
    EMAIL_HOST: str = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USERNAME: str = os.environ.get("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "")
    EMAIL_USE_TLS: bool = os.environ.get("EMAIL_USE_TLS", "True") == "True"
    EMAIL_USE_SSL: bool = os.environ.get("EMAIL_USE_SSL", "False") == "True"

    # App metadata
    PROJECT_NAME: str = "TimeGlobe WhatsApp Assistant API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "TimeGlobe WhatsApp Assistant API powered by 360dialog"
    ALLOWED_ORIGINS: str = "*"


settings = Settings()
