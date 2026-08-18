from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ObservatoryStats(BaseModel):
    total_projects: int
    total_participants: int
    total_hackathons: int
    total_jobs_created: int
    total_funding_raised: float
    total_revenue_generated: float

class TimeSeriesPoint(BaseModel):
    date: str
    value: float

class TrendNode(BaseModel):
    id: str
    name: str
    value: int
    trend_percentage: float
    time_series: List[TimeSeriesPoint]

class DrillDownResponse(BaseModel):
    level: str # 'technology', 'geography', 'domain', 'organization', 'challenge', 'project', 'outcome'
    nodes: List[TrendNode]
