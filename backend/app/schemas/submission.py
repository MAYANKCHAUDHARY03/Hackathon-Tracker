from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, AnyUrl

class SubmissionRequirementBase(BaseModel):
    title: str
    description: str | None = None
    requirement_type: str = "url"
    is_required: bool = True
    sequence: int
    validation_rules: dict | None = None

class SubmissionRequirementCreate(SubmissionRequirementBase):
    pass

class SubmissionRequirementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    requirement_type: str | None = None
    is_required: bool | None = None
    sequence: int | None = None
    validation_rules: dict | None = None

class SubmissionRequirementResponse(SubmissionRequirementBase):
    id: UUID
    workspace_id: UUID
    hackathon_id: UUID
    round_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionItemBase(BaseModel):
    requirement_id: UUID
    content: str | None = None

class SubmissionItemCreate(SubmissionItemBase):
    pass

class SubmissionItemUpdate(BaseModel):
    content: str | None = None

class SubmissionItemResponse(SubmissionItemBase):
    id: UUID
    workspace_id: UUID
    submission_id: UUID
    is_valid: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RoundSubmissionBase(BaseModel):
    status: str = "draft"

class RoundSubmissionUpdate(RoundSubmissionBase):
    pass

class RoundSubmissionResponse(RoundSubmissionBase):
    id: UUID
    workspace_id: UUID
    hackathon_id: UUID
    round_id: UUID
    team_id: UUID
    snapshot: dict | None = None
    submitted_at: datetime | None = None
    locked_at: datetime | None = None
    locked_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    
    items: list[SubmissionItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
