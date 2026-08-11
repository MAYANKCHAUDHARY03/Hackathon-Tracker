from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from uuid import UUID

class NetworkResolveRequest(BaseModel):
    query: str
    target_type: Optional[str] = None # e.g. "hackathon", "challenge", "project", "user", "mentor"
    include_impact_metrics: bool = False

class NetworkNode(BaseModel):
    id: str
    type: str
    name: str
    metadata: Dict[str, Any]

class NetworkEdge(BaseModel):
    source: str
    target: str
    relation: str

class NetworkResolveResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
