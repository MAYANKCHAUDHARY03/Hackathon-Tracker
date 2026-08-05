from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    hackathon_id: uuid.UUID

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
