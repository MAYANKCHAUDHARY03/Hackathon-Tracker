from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CalendarEvent(BaseModel):
    id: str
    title: str
    description: str | None = None
    event_type: str  # hackathon_start, hackathon_end, registration_deadline, round_start, round_end, round_result, deadline
    date: datetime
    hackathon_id: UUID
    hackathon_name: str
    color: str
    is_hard_deadline: bool = False

    model_config = ConfigDict(from_attributes=True)
