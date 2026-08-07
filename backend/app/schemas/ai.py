from pydantic import BaseModel
from typing import Dict, Any, List

class AIProjectSummaryResponse(BaseModel):
    summary: str

class AIHealthAnalysisResponse(BaseModel):
    health_status: str
    risk_score: int
    recommendations: List[str]
