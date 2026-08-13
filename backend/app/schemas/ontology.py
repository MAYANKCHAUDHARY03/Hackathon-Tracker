from typing import Any, Dict, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.ontology import EntityType

class UniversalEntityBase(BaseModel):
    entity_type: EntityType
    source: Optional[str] = "manual"
    verification_level: Optional[str] = "unverified"
    visibility: Optional[str] = "public"
    properties: Dict[str, Any] = Field(default_factory=dict)

class UniversalEntityCreate(UniversalEntityBase):
    owner_id: Optional[uuid.UUID] = None

class UniversalEntityUpdate(BaseModel):
    source: Optional[str] = None
    verification_level: Optional[str] = None
    visibility: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    owner_id: Optional[uuid.UUID] = None

class UniversalEntityResponse(UniversalEntityBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    owner_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
