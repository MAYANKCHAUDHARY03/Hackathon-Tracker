from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import uuid

class Alert(BaseModel):
    id: uuid.UUID
    severity: str # CRITICAL, WARNING, INFO
    message: str
    source: str # e.g. "Mentor Copilot", "Event Stream"
    timestamp: datetime

class ActiveProgramStat(BaseModel):
    program_id: uuid.UUID
    name: str
    active_teams: int
    pending_evaluations: int
    at_risk_projects: int

class OperationsCenterStatus(BaseModel):
    total_active_programs: int
    total_active_users: int
    total_pending_evaluations: int
    critical_incidents: int
    active_programs: List[ActiveProgramStat]
    live_alerts: List[Alert]
