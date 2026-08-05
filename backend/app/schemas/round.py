from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class HackathonRoundBase(BaseModel):
    name: str
    description: str | None = None
    round_type: str = "custom"
    sequence: int
    status: str = "upcoming"
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    result_at: datetime | None = None

class HackathonRoundCreate(HackathonRoundBase):
    pass

class HackathonRoundUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    round_type: str | None = None
    sequence: int | None = None
    status: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    result_at: datetime | None = None

class HackathonRoundResponse(HackathonRoundBase):
    id: UUID
    workspace_id: UUID
    hackathon_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DeadlineBase(BaseModel):
    name: str
    description: str | None = None
    deadline_type: str = "general"
    due_at: datetime
    is_hard_deadline: bool = False
    source_url: str | None = None
    round_id: UUID | None = None

class DeadlineCreate(DeadlineBase):
    pass

class DeadlineUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    deadline_type: str | None = None
    due_at: datetime | None = None
    is_hard_deadline: bool | None = None
    source_url: str | None = None
    round_id: UUID | None = None

class DeadlineResponse(DeadlineBase):
    id: UUID
    workspace_id: UUID
    hackathon_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RoundProgressBase(BaseModel):
    status: str = "not_started"
    score: float | None = None
    score_max: float | None = None
    feedback: str | None = None
    decision_notes: str | None = None

class RoundProgressUpdate(RoundProgressBase):
    pass

class RoundProgressResponse(RoundProgressBase):
    id: UUID
    workspace_id: UUID
    hackathon_id: UUID
    round_id: UUID
    team_id: UUID
    submitted_at: datetime | None = None
    decided_at: datetime | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
