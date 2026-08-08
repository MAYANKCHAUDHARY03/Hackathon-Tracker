from pydantic import BaseModel
from typing import Dict, Any

class WorkspaceAnalyticsSummary(BaseModel):
    total_hackathons: int
    active_hackathons: int
    total_projects: int
    total_teams: int
    total_users: int
    tasks_completed: int
    tasks_pending: int
    recent_activity_count: int
    metadata: Dict[str, Any] = {}

class AnalyticsOverview(BaseModel):
    total_users: int
    total_teams: int
    total_projects: int
    total_submissions: int

class AnalyticsDemographics(BaseModel):
    skills_distribution: Dict[str, int]
    roles_distribution: Dict[str, int]

class ScoreDistribution(BaseModel):
    range_0_20: int
    range_21_40: int
    range_41_60: int
    range_61_80: int
    range_81_100: int

class AnalyticsEvaluations(BaseModel):
    average_score: float
    total_evaluations: int
    score_distribution: ScoreDistribution
