from sqlalchemy import ForeignKey, Column, String, DateTime
from sqlalchemy import Enum as SqlEnum
from datetime import datetime
import uuid

from src.db.db_enum import WorkflowState, WorkflowType
from .base import Base  # Import shared Base

class Workflow(Base):
    __tablename__ = 'workflow'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey('event.id'), nullable=False)
    workflow_type = Column(String, nullable=False)
    workflow_state = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
