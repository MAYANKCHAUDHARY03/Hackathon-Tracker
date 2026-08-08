from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class SearchResultItem(BaseModel):
    id: UUID
    type: str = Field(..., description="Entity type: hackathon, project, team, task")
    title: str = Field(..., description="Name or title of the entity")
    description: Optional[str] = None
    url: str = Field(..., description="Frontend URL for the entity")
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context depending on entity type")
    graph_context: Optional[Dict[str, Any]] = Field(default=None, description="Connected graph entities from Phase 19 traversal")
class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total: int
