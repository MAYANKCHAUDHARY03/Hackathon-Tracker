from pydantic import BaseModel, HttpUrl
from typing import List
from uuid import UUID
from datetime import datetime

class DeveloperAppBase(BaseModel):
    name: str
    redirect_uris: List[str]

class DeveloperAppCreate(DeveloperAppBase):
    pass

class DeveloperAppResponse(DeveloperAppBase):
    id: UUID
    workspace_id: UUID
    client_id: str
    client_secret: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WebhookEndpointBase(BaseModel):
    url: HttpUrl
    events: List[str]

class WebhookEndpointCreate(WebhookEndpointBase):
    pass

class WebhookEndpointResponse(WebhookEndpointBase):
    id: UUID
    workspace_id: UUID
    secret: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
