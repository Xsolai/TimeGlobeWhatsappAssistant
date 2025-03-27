from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from ..core.config import settings
from contextlib import contextmanager
from ..models.base import Base
from ..models.customer_model import CustomerModel
from ..logger import main_logger


def verify_customers_table():
    """Verify that the customers table exists, create it if it doesn't."""
    try:
        inspector = inspect(engine)
        if 'Customers' not in inspector.get_table_names():
            main_logger.info("Customers table not found, creating it...")
            CustomerModel.__table__.create(engine)
            main_logger.info("Customers table created successfully")
        else:
            main_logger.info("Customers table already exists")
    except Exception as e:
        main_logger.error(f"Error verifying/creating customers table: {str(e)}")
        raise Exception(f"Failed to verify/create customers table: {str(e)}")


def init_db():
    """Initialize database and create tables if they don't exist."""
    try:
        main_logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        verify_customers_table()  # Explicitly verify customers table
        main_logger.info("Database initialized successfully")
    except Exception as e:
        main_logger.error(f"Error initializing database: {str(e)}")
        raise Exception(f"Failed to initialize database: {str(e)}")


engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
