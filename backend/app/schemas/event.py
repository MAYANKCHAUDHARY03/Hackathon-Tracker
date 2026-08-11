from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

class EventBase(BaseModel):
    workspace_id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    entity_type: str
    entity_id: Optional[str] = None
    event_type: str
    source: str = "api"
    correlation_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: uuid.UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
