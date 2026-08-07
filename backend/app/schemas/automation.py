from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AutomationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    action_type: str
    conditions: Dict[str, Any]
    enabled: bool = True

class AutomationRuleCreate(AutomationRuleBase):
    organization_id: UUID
    workspace_id: Optional[UUID] = None

class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    action_type: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    archived_at: Optional[datetime] = None

class AutomationRuleResponse(AutomationRuleBase):
    id: UUID
    organization_id: UUID
    workspace_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    archived_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AutomationExecutionBase(BaseModel):
    triggering_event: Dict[str, Any]
    status: str
    attempts: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    correlation_id: Optional[str] = None

class AutomationExecutionCreate(AutomationExecutionBase):
    pass

class AutomationExecutionUpdate(BaseModel):
    status: Optional[str] = None
    attempts: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class AutomationExecutionResponse(AutomationExecutionBase):
    id: UUID
    rule_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
