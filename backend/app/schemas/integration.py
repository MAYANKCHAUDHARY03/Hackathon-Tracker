from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

class ExternalSubmissionConnectionBase(BaseModel):
    provider_name: str
    credentials: Dict[str, Any] = Field(..., description="API keys or tokens required for integration")
    is_active: bool = True

class ExternalSubmissionConnectionCreate(ExternalSubmissionConnectionBase):
    pass

class ExternalSubmissionConnectionUpdate(BaseModel):
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ExternalSubmissionConnectionResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    provider_name: str
    is_active: bool
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncSubmissionsRequest(BaseModel):
    hackathon_reference: str

class SyncSubmissionsResponse(BaseModel):
    synced_count: int
    failed_count: int
    message: str
