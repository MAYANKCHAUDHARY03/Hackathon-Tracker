import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class GraphEdgeBase(BaseModel):
    source_type: str
    source_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    relation_type: str
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    provenance: Optional[str] = "user-provided"
    confidence: Optional[float] = 1.0
    edge_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GraphEdgeCreate(GraphEdgeBase):
    pass

class GraphEdgeResponse(GraphEdgeBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)

class GraphTraversalResult(BaseModel):
    path: List[Dict[str, Any]]
    nodes: Dict[str, Any] # Map of id to node details
