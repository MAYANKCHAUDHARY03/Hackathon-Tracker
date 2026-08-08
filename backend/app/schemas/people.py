from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, AnyHttpUrl

class PersonBase(BaseModel):
    full_name: str
    organisation: str | None = None
    designation: str | None = None
    expertise_areas: list[str] | None = None
    bio: str | None = None
    public_profile_url: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    visibility: str = "workspace"

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    full_name: str | None = None
    organisation: str | None = None
    designation: str | None = None
    expertise_areas: list[str] | None = None
    bio: str | None = None
    public_profile_url: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    visibility: str | None = None

class PersonResponse(PersonBase):
    id: UUID
    workspace_id: UUID
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MentorAssignmentBase(BaseModel):
    hackathon_id: UUID
    round_id: UUID | None = None
    team_id: UUID | None = None
    mentor_id: UUID
    topic: str | None = None
    session_at: datetime | None = None
    notes: str | None = None
    status: str = "planned"

class MentorAssignmentCreate(MentorAssignmentBase):
    pass

class MentorAssignmentUpdate(BaseModel):
    round_id: UUID | None = None
    team_id: UUID | None = None
    mentor_id: UUID | None = None
    topic: str | None = None
    session_at: datetime | None = None
    notes: str | None = None
    status: str | None = None

class MentorAssignmentResponse(MentorAssignmentBase):
    id: UUID
    workspace_id: UUID
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    mentor: PersonResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class JudgeAssignmentBase(BaseModel):
    hackathon_id: UUID
    round_id: UUID | None = None
    judge_id: UUID
    role: str | None = None
    panel_name: str | None = None
    assignment_notes: str | None = None

class JudgeAssignmentCreate(JudgeAssignmentBase):
    pass

class JudgeAssignmentUpdate(BaseModel):
    round_id: UUID | None = None
    judge_id: UUID | None = None
    role: str | None = None
    panel_name: str | None = None
    assignment_notes: str | None = None

class JudgeAssignmentResponse(JudgeAssignmentBase):
    id: UUID
    workspace_id: UUID
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    judge: PersonResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class CsvImportResult(BaseModel):
    total_processed: int
    successful: int
    failed: int
    errors: list[str]
