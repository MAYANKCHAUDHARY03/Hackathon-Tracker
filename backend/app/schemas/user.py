from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from app.schemas.workspace import WorkspaceResponse

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    is_active: bool = True
    avatar_url: Optional[str] = None
    github_handle: Optional[str] = None
    linkedin_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
