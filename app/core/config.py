from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    # DATABASE_URL: str = "sqlite:///./app.db"
    # SECRETE_KEY = secrets.token_urlsafe(32)
    from_whatsapp_number: str
    account_sid: str
    auth_token: str
    TWILIO_API_URL: str
    WABA_ID: str
    TIME_GLOBE_LOGIN_USERNAME: str
    TIME_GLOBE_LOGIN_PASSWORD: str
    TIME_GLOBE_BASE_URL: str
    OPENAI_ASSISTANT_ID: str
    OPENAI_API_KEY: str
    TIME_GLOBE_API_KEY: str
    # ACCESS_TOKEN_EXPIRE_TIME: int = 30
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
