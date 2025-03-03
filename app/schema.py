from pydantic import BaseModel, UUID4,Field
from typing import Optional, Dict
from enum import Enum
from datetime import datetime

class TriggerType(str, Enum):
    SCHEDULED = "scheduled"
    API = "api"

class TriggerCreate(BaseModel):
    name: str
    type: TriggerType
    schedule: Optional[int] = None  # Only for scheduled triggers
    payload: Optional[Dict[str, str]] = None  # Only for API triggers
    recurring: Optional[bool] = False
    test: Optional[bool] = False

class TriggerResponse(TriggerCreate):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True  # Ensures SQLAlchemy models map correctly
        orm = True

class TriggerUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Updated Trigger Name")
    schedule: Optional[int] = Field(None, example=3600)
    recurring: Optional[bool] = Field(None, example=True)
    payload: Optional[Dict] = Field(None, example={"key1": "value1", "key2": "value2"})

    class Config:
        orm_mode = True

class EventLogResponse(BaseModel):
    id: UUID4
    trigger_id: UUID4
    executed_at: datetime
    payload: Optional[Dict[str, str]] = None
    status: str  # "active", "archived", "deleted"
    trigger: Optional[TriggerResponse]

    class Config:
        from_attributes = True
        orm = True


class TriggerTestRequest(BaseModel):
    trigger_id: UUID4
    payload: Optional[Dict[str, str]] = None  # Test payload (only for API triggers)


