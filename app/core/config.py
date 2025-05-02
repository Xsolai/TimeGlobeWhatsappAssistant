from pydantic_settings import BaseSettings
from .env import load_env

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
    DIALOG360_API_URL: str = env.get("DIALOG360_API_URL", "https://waba.360dialog.io/v1")
    DIALOG360_PHONE_NUMBER: str = env.get("DIALOG360_PHONE_NUMBER", "")

    # TimeGlobe Settings
    TIME_GLOBE_BASE_URL: str = env.get("TIME_GLOBE_BASE_URL", "")
    TIME_GLOBE_LOGIN_USERNAME: str = env.get("TIME_GLOBE_LOGIN_USERNAME", "")
    TIME_GLOBE_LOGIN_PASSWORD: str = env.get("TIME_GLOBE_LOGIN_PASSWORD", "")
    TIME_GLOBE_API_KEY: str = env.get("TIME_GLOBE_API_KEY", "")
    WABA_ID: str = env.get("WABA_ID", "")

    # OpenAI Settings
    OPENAI_API_KEY: str = env.get("OPENAI_API_KEY", "")
    OPENAI_ASSISTANT_ID: str = env.get("OPENAI_ASSISTANT_ID", "")

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
    PROJECT_NAME: str = "TimeGlobe WhatsApp Assistant API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "TimeGlobe WhatsApp Assistant API powered by 360dialog"
    ALLOWED_ORIGINS: str = "*"


settings = Settings()
