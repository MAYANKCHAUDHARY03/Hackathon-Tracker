from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List

class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    metadata_json: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    workspace_id: UUID
    actor_id: Optional[UUID] = None

class AuditLogResponse(AuditLogBase):
    id: UUID
    workspace_id: UUID
    actor_id: Optional[UUID] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
