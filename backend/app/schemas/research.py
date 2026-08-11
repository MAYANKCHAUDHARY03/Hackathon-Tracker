from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
import uuid

class ResearchLinkBase(BaseModel):
    type: str = Field(..., description="Type of research link: paper, patent, dataset, repo, institution")
    title: str
    url: Optional[str] = None
    identifier: Optional[str] = Field(None, description="DOI, patent number, etc.")
    authors: Optional[List[str]] = None
    publication_date: Optional[datetime] = None

class ResearchLinkCreate(ResearchLinkBase):
    project_id: uuid.UUID

class ResearchLinkUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    identifier: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[datetime] = None

class ResearchLinkResponse(ResearchLinkBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    project_id: uuid.UUID
    provenance: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
