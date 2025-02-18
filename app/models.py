from sqlalchemy import Column, String, Enum, JSON, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base, engine
import enum

class TriggerType(str, enum.Enum):
    SCHEDULED = "scheduled"
    API = "api"

class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(Enum(TriggerType), nullable=False)
    schedule = Column(Integer, nullable=True)  # Cron format for scheduled triggers
    payload = Column(JSON, nullable=True)  # API trigger payload
    recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    task_id = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    test = Column(Boolean, default=False)

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trigger_id = Column(UUID(as_uuid=True), ForeignKey("triggers.id"), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON, nullable=True) # Not required, will remove in next iteration
    status = Column(String, default="active")  # active -> archived -> deleted

    trigger = relationship("Trigger", backref="event_logs")

def init_db():
    Base.metadata.create_all(bind=engine)
