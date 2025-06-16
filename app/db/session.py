from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..core.config import settings
from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base


# Define the Base class
Base = declarative_base()
engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
