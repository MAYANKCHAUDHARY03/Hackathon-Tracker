from pydantic import BaseModel
from typing import Dict, Any

class WorkspaceAnalyticsSummary(BaseModel):
    total_hackathons: int
    active_hackathons: int
    total_projects: int
    total_teams: int
    total_users: int
    tasks_completed: int
    tasks_pending: int
    recent_activity_count: int
    metadata: Dict[str, Any] = {}
