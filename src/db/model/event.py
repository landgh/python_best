from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone  # Import datetime for timestamp handling
import uuid
from sqlalchemy import Enum as SqlEnum  # Alias to avoid conflict with Python's Enum
from src.db.db_enum import EventType
from .base import Base  # Import shared Base

class Event(Base):
    __tablename__ = 'event'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    data_source = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc),  nullable=False)
