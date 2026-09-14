from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime, timezone

class ActivityEventBase(BaseModel):
    action: str
    entity_type: str
    entity_id: uuid.UUID | None = None
    safe_edge_metadata: dict | None = None

class ActivityEventResponse(ActivityEventBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    project_id: uuid.UUID | None = None
    actor_id: uuid.UUID | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
