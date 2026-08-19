from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.portable_project import ProjectStage
from app.models.portable_identity import VisibilityTier

class PortableProjectIdentityBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    current_stage: ProjectStage = ProjectStage.HACKATHON
    visibility: VisibilityTier = VisibilityTier.PRIVATE

class PortableProjectIdentityCreate(PortableProjectIdentityBase):
    pass

class PortableProjectIdentityResponse(PortableProjectIdentityBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectStageTransitionBase(BaseModel):
    from_stage: Optional[ProjectStage] = None
    to_stage: ProjectStage
    organization_id: Optional[UUID] = None
    program_context_id: Optional[UUID] = None
    program_context_type: Optional[str] = None
    notes: Optional[str] = None

class ProjectStageTransitionCreate(ProjectStageTransitionBase):
    pass

class ProjectStageTransitionResponse(ProjectStageTransitionBase):
    id: UUID
    portable_project_id: UUID
    transition_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PortableProjectHistoryResponse(BaseModel):
    project: PortableProjectIdentityResponse
    transitions: List[ProjectStageTransitionResponse]
