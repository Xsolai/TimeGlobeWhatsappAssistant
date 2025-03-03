from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settingss

engine = create_async_engine(settingss.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
