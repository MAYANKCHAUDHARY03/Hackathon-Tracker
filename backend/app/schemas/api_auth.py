import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class APIKeyCreate(BaseModel):
    name: str = Field(..., description="A friendly name for the API key")
    scopes: list[str] = Field(default=[], description="List of permission scopes")

class APIKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    scopes: list[str]
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class APIKeyCreateResponse(APIKeyResponse):
    key: str = Field(..., description="The full, unhashed API key. This will never be shown again.")

class OAuthAppCreate(BaseModel):
    name: str
    description: str | None = None
    homepage_url: str | None = None
    callback_urls: list[str] = Field(default=[])

class OAuthAppResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    homepage_url: str | None
    callback_urls: list[str]
    client_id: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OAuthAppCreateResponse(OAuthAppResponse):
    client_secret: str = Field(..., description="The unhashed client secret. This will never be shown again.")
