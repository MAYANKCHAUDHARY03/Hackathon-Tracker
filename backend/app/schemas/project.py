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
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
