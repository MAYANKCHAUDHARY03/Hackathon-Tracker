from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class CustomMetricBase(BaseModel):
    name: str
    description: Optional[str] = None
    unit: str

class CustomMetricCreate(CustomMetricBase):
    pass

class CustomMetricResponse(CustomMetricBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectImpactBase(BaseModel):
    stage: str = Field(..., description="Participation, Project, Prototype, Pilot, Deployment, Startup, Impact")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)
    jobs_created: int = 0
    funding_raised: float = 0.0
    revenue_generated: float = 0.0

class ProjectImpactUpdate(BaseModel):
    stage: Optional[str] = None
    custom_metrics: Optional[Dict[str, Any]] = None
    jobs_created: Optional[int] = None
    funding_raised: Optional[float] = None
    revenue_generated: Optional[float] = None

class ProjectImpactResponse(ProjectImpactBase):
    id: UUID
    workspace_id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FunnelMetricsResponse(BaseModel):
    participation: int
    projects: int
    prototypes: int
    pilots: int
    deployments: int
    startups: int
    jobs: int
