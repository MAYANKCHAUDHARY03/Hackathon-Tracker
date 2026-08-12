from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.governance import DSRType, DSRStatus

# DSR Schemas
class DSRBase(BaseModel):
    request_type: DSRType
    details: Optional[str] = None

class DSRCreate(DSRBase):
    pass

class DSRResponse(DSRBase):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    status: DSRStatus
    resolution_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Consent Schemas
class ConsentBase(BaseModel):
    consent_type: str
    status: str

class ConsentCreate(ConsentBase):
    pass

class ConsentResponse(ConsentBase):
    id: UUID
    user_id: UUID
    workspace_id: UUID
    ip_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Policy Schemas
class WorkspacePolicy(BaseModel):
    data_residency: str = "US"
    retention_days: int = 365
    ai_consent: bool = False

class WorkspacePolicyUpdate(WorkspacePolicy):
    pass

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    actor_id: Optional[UUID] = None
    action: str
    target_resource: Optional[str] = None
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
