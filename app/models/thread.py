from sqlalchemy import Column, String
from .base import Base


class ThreadModel(Base):
    __tablename__ = "Threads"

    mobile_number = Column(String, primary_key=True)
    thread_id = Column(String, nullable=False)
