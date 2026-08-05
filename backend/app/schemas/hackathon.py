from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator, model_validator
from typing import Optional, List
from uuid import UUID

class HackathonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    organiser: Optional[str] = Field(None, max_length=255)
    official_url: Optional[HttpUrl] = None
    mode: str = Field(default="online", description="Must be online, offline, or hybrid")
    location: Optional[str] = None
    registration_deadline: datetime
    start_date: datetime
    end_date: datetime
    max_team_size: int = Field(default=1, gt=0)
    status: str = Field(default="draft", description="Must be draft, upcoming, active, completed, or archived")

    @validator("mode")
    def validate_mode(cls, v):
        allowed = {"online", "offline", "hybrid"}
        if v not in allowed:
            raise ValueError(f"Mode must be one of {allowed}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        allowed = {"draft", "upcoming", "active", "completed", "archived"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        if self.registration_deadline > self.start_date:
            raise ValueError("registration_deadline must be before or equal to start_date")
        return self

    @model_validator(mode="after")
    def validate_location(self):
        if self.mode in {"offline", "hybrid"} and not self.location:
            raise ValueError(f"location is required for mode '{self.mode}'")
        return self

class HackathonCreate(HackathonBase):
    pass

class HackathonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    organiser: Optional[str] = Field(None, max_length=255)
    official_url: Optional[HttpUrl] = None
    mode: Optional[str] = None
    location: Optional[str] = None
    registration_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_team_size: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None

    @validator("mode")
    def validate_mode(cls, v):
        if v is None: return v
        allowed = {"online", "offline", "hybrid"}
        if v not in allowed:
            raise ValueError(f"Mode must be one of {allowed}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        if v is None: return v
        allowed = {"draft", "upcoming", "active", "completed", "archived"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    # We skip complex cross-field validation on partial updates since missing fields 
    # make it difficult without database context. The service layer will enforce date constraints on update.

class HackathonResponse(HackathonBase):
    id: UUID
    workspace_id: UUID
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]

    class Config:
        from_attributes = True

class HackathonListResponse(BaseModel):
    items: List[HackathonResponse]
    total: int
