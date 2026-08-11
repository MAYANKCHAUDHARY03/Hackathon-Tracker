from pydantic import BaseModel

class ObservatoryStats(BaseModel):
    total_projects: int
    total_participants: int
    total_hackathons: int
    total_jobs_created: int
    total_funding_raised: float
    total_revenue_generated: float
