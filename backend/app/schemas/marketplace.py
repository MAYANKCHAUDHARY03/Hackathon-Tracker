import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MarketplaceProjectItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    status: str
    description: Optional[str] = None
    technologies: List[str] = []
    hackathon_origin: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class MarketplacePartnerItem(BaseModel):
    id: uuid.UUID
    type: str # "Organization", "Sponsor", "Person"
    name: str
    description: Optional[str] = None
    resources_offered: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)

class MarketplaceProjectsResponse(BaseModel):
    projects: List[MarketplaceProjectItem]

class MarketplacePartnersResponse(BaseModel):
    partners: List[MarketplacePartnerItem]
