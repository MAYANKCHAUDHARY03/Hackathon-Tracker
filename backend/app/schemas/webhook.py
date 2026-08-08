from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any

class WebhookSubscriptionBase(BaseModel):
    url: str
    events: List[str]
    secret: Optional[str] = None
    is_active: bool = True

class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    pass

class WebhookSubscriptionUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WebhookDeliveryResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    event_type: str
    payload: Any
    status_code: Optional[int]
    response_body: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
