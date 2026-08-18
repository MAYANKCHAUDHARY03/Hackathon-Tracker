from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class MentorRecommendedResource(BaseModel):
    title: str
    url: str
    reason: str

class MentorCopilotBrief(BaseModel):
    project_id: UUID
    team_name: str
    project_title: str
    progress_summary: str
    recent_activity: List[str]
    flagged_blockers: List[str]
    suggested_agenda: List[str]
    recommended_resources: List[MentorRecommendedResource]
