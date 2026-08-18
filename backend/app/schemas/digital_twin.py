from pydantic import BaseModel
from typing import Dict, Any, List
from uuid import UUID

class DigitalTwinSimulationRequest(BaseModel):
    base_hackathon_id: UUID | None = None
    target_teams_count: int | None = None
    target_participants_count: int | None = None
    target_projects_count: int | None = None
    complexity_multiplier: float = 1.0

class ResourceProjection(BaseModel):
    category: str
    current_capacity: int
    projected_requirement: int
    gap: int
    risk_level: str

class DigitalTwinSimulationResponse(BaseModel):
    projected_judges_needed: int
    projected_mentors_needed: int
    projected_infrastructure_cost: float
    resource_projections: List[ResourceProjection]
    insights: List[str]
