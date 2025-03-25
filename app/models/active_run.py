from sqlalchemy import Column, String, ForeignKey
from .base import Base


class ActiveRunModel(Base):
    __tablename__ = "ActiveRuns"

    thread_id = Column(String, ForeignKey("Threads.thread_id"), primary_key=True)
    run_id = Column(String, nullable=False)
