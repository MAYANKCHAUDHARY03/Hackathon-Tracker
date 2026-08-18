from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from app.models.portable_identity import VisibilityTier

class VerifiedSkillSchema(BaseModel):
    id: UUID
    identity_id: UUID
    skill_name: str
    verification_level: str
    evidence_trail: List[Any]
    
    class Config:
        from_attributes = True

class PortableIdentityBase(BaseModel):
    visibility_projects: VisibilityTier = VisibilityTier.PRIVATE
    visibility_achievements: VisibilityTier = VisibilityTier.PRIVATE
    visibility_skills: VisibilityTier = VisibilityTier.PRIVATE
    selective_sharing_workspaces: List[str] = Field(default_factory=list)

class PortableIdentityUpdate(BaseModel):
    visibility_projects: Optional[VisibilityTier] = None
    visibility_achievements: Optional[VisibilityTier] = None
    visibility_skills: Optional[VisibilityTier] = None
    selective_sharing_workspaces: Optional[List[str]] = None

class PortableIdentityResponse(PortableIdentityBase):
    id: UUID
    user_id: UUID
    total_projects: int
    total_achievements: int
    skills: List[VerifiedSkillSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
