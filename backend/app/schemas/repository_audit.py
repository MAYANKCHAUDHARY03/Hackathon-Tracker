from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class RepositoryAuditCreate(BaseModel):
    project_id: UUID
    cyclomatic_complexity_score: Optional[float] = None
    sast_vulnerabilities_count: int = 0
    guideline_adherence_score: Optional[float] = None
    sast_findings: List[Any] = []
    guideline_violations: List[Any] = []
    audited_by_agent_id: Optional[str] = None
    status: str = "COMPLETED"

class RepositoryAuditResponse(RepositoryAuditCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
