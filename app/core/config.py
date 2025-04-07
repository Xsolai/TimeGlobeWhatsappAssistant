from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./time_globe_assistant.db"
    SECRETE_KEY: str = secrets.token_urlsafe(32)
    FROM_WHATSAPP_NUMBER: str
    ACCOUNT_SID: str
    AUTH_TOKEN: str
    TWILIO_API_URL: str
    WABA_ID: str
    TIME_GLOBE_LOGIN_USERNAME: str
    TIME_GLOBE_LOGIN_PASSWORD: str
    TIME_GLOBE_BASE_URL: str
    TWILIO_MESSAGING_SERVICE_SID: str
    OPENAI_ASSISTANT_ID: str
    OPENAI_API_KEY: str
    TIME_GLOBE_API_KEY: str
    ACCESS_TOKEN_EXPIRE_TIME: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
