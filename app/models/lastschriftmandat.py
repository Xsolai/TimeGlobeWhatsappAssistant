from sqlalchemy import Column, String, DateTime, ForeignKey, LargeBinary, Text
import uuid
from datetime import datetime, timezone
from .base import Base
from sqlalchemy.orm import relationship

class Lastschriftmandat(Base):
    __tablename__ = "lastschriftmandats"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    pdf_file = Column(LargeBinary, nullable=False)  # Store the PDF directly
    file_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationship
    business = relationship("Business", back_populates="lastschriftmandat") 