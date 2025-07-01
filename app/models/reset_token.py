from sqlalchemy import Column, String, DateTime, Index
import uuid
from datetime import datetime, timedelta
from ..utils.timezone_util import BERLIN_TZ
from .base import Base


class ResetToken(Base):
    __tablename__ = "reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String, nullable=False, unique=True, index=True)
    business_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(BERLIN_TZ))
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.now(BERLIN_TZ) + timedelta(hours=24)

    @property
    def is_expired(self):
        return datetime.now(BERLIN_TZ) > self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None


# Add composite index for cleanup queries
__table_args__ = (
    Index('idx_reset_token_business_expires', 'business_id', 'expires_at'),
) 