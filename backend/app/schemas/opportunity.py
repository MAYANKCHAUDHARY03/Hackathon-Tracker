from typing import List
from pydantic import BaseModel, Field

class OpportunityMatch(BaseModel):
    target_id: str = Field(..., description="The ID of the matched opportunity target (e.g. Hackathon, Team)")
    target_type: str = Field(..., description="The type of the matched opportunity (e.g. 'Hackathon', 'Team', 'Project')")
    target_name: str = Field(..., description="The name of the matched opportunity")
    score: int = Field(..., description="Match score from 0-100")
    reasons: List[str] = Field(default_factory=list, description="Reasons why this match was made")
    evidence: List[str] = Field(default_factory=list, description="Verifiable evidence from the graph (e.g. overlapping skills, past projects)")
    limitations: List[str] = Field(default_factory=list, description="Limitations or reasons why this match might not be perfect (e.g. missing skills)")

class OpportunityMatchResponse(BaseModel):
    matches: List[OpportunityMatch]
