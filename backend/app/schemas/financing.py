from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class FundingOpportunityBase(BaseModel):
    title: str
    opportunity_type: str
    amount: float | None = None
    currency: str = "USD"
    sponsor_id: UUID | None = None
    sponsor_name: str
    criteria: dict = {}
    description: str

class FundingOpportunityCreate(FundingOpportunityBase):
    pass

class FundingOpportunityResponse(FundingOpportunityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OpportunityMatchResponse(BaseModel):
    opportunity: FundingOpportunityResponse
    match_score: float
    matched_criteria: list[str]
    missing_criteria: list[str]
