from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

class WorkspaceBase(BaseModel):
    name: str
    slug: str
    settings: dict = {}

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceResponse(WorkspaceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkspaceInvitationCreate(BaseModel):
    email: str
    role: str

class WorkspaceInvitationResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    email: str
    workspace_role: str
    invited_by: UUID
    token_hash: str
    status: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
