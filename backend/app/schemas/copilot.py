from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class CopilotQuery(BaseModel):
    query: str = Field(..., description="The user's natural language question")

class SourceEntity(BaseModel):
    id: UUID
    type: str = Field(..., description="Entity type, e.g., project, team")
    name: str = Field(..., description="Name or title of the entity")

class CopilotResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer")
    evidence: List[str] = Field(..., description="List of evidence strings extracted from context")
    source_entities: List[SourceEntity] = Field(..., description="The entities from the knowledge graph used as context")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    recommended_action: Optional[str] = Field(None, description="Suggested next action or query")
