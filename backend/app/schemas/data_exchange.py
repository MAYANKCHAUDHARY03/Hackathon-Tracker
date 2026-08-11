from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ExportHackathonV1(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    mode: str
    location: Optional[str] = None
    registration_deadline: datetime
    start_date: datetime
    end_date: datetime
    timezone: str
    max_team_size: int
    status: str
    program_type: str

class ExportProjectV1(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    solution_summary: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None
    demo_url: Optional[str] = None
    status: str

class ExportOrganizationV1(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    website: Optional[str] = None

class InnovationSchemaV1(BaseModel):
    version: str = "1.0"
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    hackathons: List[ExportHackathonV1] = []
    projects: List[ExportProjectV1] = []
    organizations: List[ExportOrganizationV1] = []
    
class ExportRequest(BaseModel):
    format: str = Field(default="json", description="json, csv, or ndjson")
    include_hackathons: bool = True
    include_projects: bool = True
    include_organizations: bool = True
