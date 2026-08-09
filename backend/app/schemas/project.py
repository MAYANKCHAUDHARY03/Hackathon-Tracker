from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    repository_url: str | None = None

class ProjectCreate(ProjectBase):
    hackathon_id: uuid.UUID | None = None

class ProjectResponse(ProjectBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    team_id: uuid.UUID
    hackathon_id: uuid.UUID | None = None
    status: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProjectTransitionCreate(BaseModel):
    state: str
    notes: str | None = None

class ProjectTransition(BaseModel):
    state: str
    transitioned_at: str
    actor_id: str
    actor_name: str
    notes: str | None = None

