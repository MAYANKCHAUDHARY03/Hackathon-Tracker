from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid
import datetime

class MatchOpportunityBase(BaseModel):
    title: str
    description: Optional[str] = None
    opportunity_type: str
    tags: List[str] = []

class MatchOpportunityCreate(MatchOpportunityBase):
    pass

class MatchOpportunityResponse(MatchOpportunityBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    provider_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MatchProfileBase(BaseModel):
    entity_type: str
    entity_id: str
    tags: List[str] = []
    needs: List[str] = []

class MatchProfileCreate(MatchProfileBase):
    pass

class MatchProfileResponse(MatchProfileBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class MatchRecommendationResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    profile_id: uuid.UUID
    opportunity_id: uuid.UUID
    score: int
    status: str
    created_at: datetime.datetime
    
    opportunity: MatchOpportunityResponse
    profile: MatchProfileResponse

    model_config = ConfigDict(from_attributes=True)
