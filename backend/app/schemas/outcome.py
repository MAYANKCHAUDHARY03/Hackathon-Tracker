from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List

class HackathonResultBase(BaseModel):
    hackathon_id: UUID
    team_id: UUID
    project_id: Optional[UUID] = None
    round_id: Optional[UUID] = None
    result_type: str = "participant"
    position: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str = "draft"
    announced_at: Optional[datetime] = None
    source_url: Optional[str] = None

class HackathonResultCreate(HackathonResultBase):
    pass

class HackathonResultUpdate(BaseModel):
    result_type: Optional[str] = None
    position: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    announced_at: Optional[datetime] = None
    source_url: Optional[str] = None
    is_verified: Optional[bool] = None
    verification_note: Optional[str] = None

class HackathonResultResponse(HackathonResultBase):
    id: UUID
    workspace_id: UUID
    is_verified: bool = False
    verification_note: Optional[str] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class RewardBase(BaseModel):
    hackathon_id: UUID
    team_id: Optional[UUID] = None
    result_id: Optional[UUID] = None
    title: str
    reward_type: str = "other"
    monetary_value: Optional[Decimal] = None
    currency: Optional[str] = None
    sponsor: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"
    received_at: Optional[datetime] = None

class RewardCreate(RewardBase):
    pass

class RewardUpdate(BaseModel):
    title: Optional[str] = None
    reward_type: Optional[str] = None
    monetary_value: Optional[Decimal] = None
    currency: Optional[str] = None
    sponsor: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    received_at: Optional[datetime] = None

class RewardResponse(RewardBase):
    id: UUID
    workspace_id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AchievementBase(BaseModel):
    user_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    hackathon_id: UUID
    project_id: Optional[UUID] = None
    result_id: Optional[UUID] = None
    achievement_type: str = "badge"
    title: str
    description: Optional[str] = None
    visibility: str = "public"
    source: Optional[str] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None

class AchievementResponse(AchievementBase):
    id: UUID
    workspace_id: UUID
    achieved_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
