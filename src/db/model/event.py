from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from .base import Base  # Import shared Base

class Event(Base):
    __tablename__ = 'events'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
