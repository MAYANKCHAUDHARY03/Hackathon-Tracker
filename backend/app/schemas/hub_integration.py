from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

class WorkspaceIntegrationBase(BaseModel):
    connector_id: str
    name: str
    is_active: bool = True
    config: Dict[str, Any] = {}

class WorkspaceIntegrationCreate(WorkspaceIntegrationBase):
    workspace_id: uuid.UUID

class WorkspaceIntegrationUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    last_sync_status: Optional[str] = None
    last_sync_error: Optional[str] = None

class WorkspaceIntegrationResponse(WorkspaceIntegrationBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    last_sync_status: Optional[str] = None
    last_sync_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConnectorInfo(BaseModel):
    id: str
    name: str
    category: str
    description: str
    auth_type: str
    config_schema: Dict[str, Any]
