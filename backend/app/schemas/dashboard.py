from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class DashboardHackathonItem(BaseModel):
    id: UUID
    name: str
    status: str
    start_date: datetime
    end_date: datetime
    registration_deadline: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DashboardSummaryResponse(BaseModel):
    total_active: int
    total_upcoming: int
    total_completed: int
    total_non_archived: int
    upcoming_deadlines: List[DashboardHackathonItem]
    nearest_upcoming_event: Optional[DashboardHackathonItem]
    recently_updated: List[DashboardHackathonItem]
