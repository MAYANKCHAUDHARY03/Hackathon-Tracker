from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    hackathon_id: uuid.UUID
    skills_needed: list[str] | None = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    skills_needed: list[str] | None = None

class TeamResponse(TeamBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
