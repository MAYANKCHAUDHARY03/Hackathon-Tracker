from pydantic import BaseModel, Field
from typing import List, Optional

class TechnologyAdoptionMetric(BaseModel):
    technology_name: str
    category: str
    project_count: int

class ProjectStatusMetric(BaseModel):
    status: str
    project_count: int

class ParticipationTrendMetric(BaseModel):
    period: str  # e.g., '2023-01'
    project_count: int

class EcosystemAnalyticsResponse(BaseModel):
    total_projects: int
    total_technologies: int
    top_technologies: List[TechnologyAdoptionMetric]
    project_status_distribution: List[ProjectStatusMetric]
    participation_trends: List[ParticipationTrendMetric]

class EcosystemOptInUpdate(BaseModel):
    ecosystem_opt_in: bool
