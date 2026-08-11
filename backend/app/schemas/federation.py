from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.federation import FederationStatus

class WorkspaceFederationBase(BaseModel):
    target_workspace_id: UUID
    shared_entities: List[str] = Field(default_factory=list)

class WorkspaceFederationCreate(WorkspaceFederationBase):
    pass

class WorkspaceFederationUpdate(BaseModel):
    status: Optional[FederationStatus] = None
    shared_entities: Optional[List[str]] = None

class WorkspaceFederationResponse(WorkspaceFederationBase):
    id: UUID
    source_workspace_id: UUID
    status: FederationStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
