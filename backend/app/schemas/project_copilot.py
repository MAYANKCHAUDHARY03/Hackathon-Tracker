from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class CopilotRecommendedAction(BaseModel):
    action_type: str  # e.g., "create_task", "schedule_reminder", "generate_checklist"
    description: str
    target_entity_id: Optional[UUID] = None
    target_entity_type: Optional[str] = None
    payload: Optional[dict] = None

class ProjectCopilotStatus(BaseModel):
    project_id: UUID
    status: str
    progress_percent: int
    risk_flags: List[str]
    detected_issues: List[str]
    recommended_actions: List[CopilotRecommendedAction]

class CopilotActionRequest(BaseModel):
    action: CopilotRecommendedAction
