from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PortfolioItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str # 'team', 'project', etc
    url: Optional[str]
    date: datetime

class UserPortfolio(BaseModel):
    user_id: str
    full_name: str
    bio: Optional[str]
    items: List[PortfolioItem]

class OrgPortfolioStats(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    startups_spawned: int
    patents_research: int
    top_technologies: List[str]

class OrgPortfolioProject(BaseModel):
    id: str
    name: str
    status: str
    technologies: List[str]
    description: Optional[str]

class OrganizationPortfolio(BaseModel):
    org_id: str
    name: str
    stats: OrgPortfolioStats
    projects: List[OrgPortfolioProject]
    startups: List[Dict[str, Any]]

class TechnologyCount(BaseModel):
    name: str
    count: int

class PortfolioMetrics(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    startups_spawned: int
    patents_filed: int
    top_technologies: List[TechnologyCount]
    total_participants: int


import uuid
from pydantic import ConfigDict
from app.schemas.project import ProjectResponse

class PortfolioBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    owner_id: uuid.UUID
    owner_type: str
    created_at: datetime
    updated_at: datetime
    
    projects: List[ProjectResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class PortfolioProjectAdd(BaseModel):
    project_id: uuid.UUID
