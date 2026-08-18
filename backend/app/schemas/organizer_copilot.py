from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class OrganizerCopilotRecommendedAction(BaseModel):
    action_type: str  # e.g., "send_reminder", "reassign_judge", "extend_deadline"
    description: str
    reason: str
    expected_impact: str
    target_entity_id: Optional[UUID] = None
    target_entity_type: Optional[str] = None
    payload: Optional[dict] = None

class OrganizerCopilotStatus(BaseModel):
    hackathon_id: UUID
    overall_health: str
    incomplete_submissions: int
    missing_demos: int
    incomplete_evaluations: int
    risk_flags: List[str]
    recommended_actions: List[OrganizerCopilotRecommendedAction]

class OrganizerCopilotActionRequest(BaseModel):
    action: OrganizerCopilotRecommendedAction
