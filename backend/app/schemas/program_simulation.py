from pydantic import BaseModel
from typing import List, Dict, Any

class ProgramSimulationRequest(BaseModel):
    participant_count: int
    team_count: int
    rounds_count: int
    judges_available: int
    mentors_available: int
    evaluation_criteria_count: int
    duration_days: int

class SimulationRisk(BaseModel):
    risk_factor: str
    severity: str
    mitigation: str

class ProgramSimulationResponse(BaseModel):
    expected_load: Dict[str, Any]
    judge_requirements: Dict[str, Any]
    mentor_requirements: Dict[str, Any]
    infrastructure_requirements: Dict[str, Any]
    projected_risks: List[SimulationRisk]
    is_viable: bool
