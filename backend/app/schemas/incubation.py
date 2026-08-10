from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Project Update Schemas
class ProjectUpdateBase(BaseModel):
    title: str
    content: str
    update_type: str
    kpi_metrics: Optional[Dict[str, Any]] = None

class ProjectUpdateCreate(ProjectUpdateBase):
    pass

class ProjectUpdateResponse(ProjectUpdateBase):
    id: uuid.UUID
    project_id: uuid.UUID
    author_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Project Document Schemas
class ProjectDocumentBase(BaseModel):
    title: str
    document_type: str
    url: str

class ProjectDocumentCreate(ProjectDocumentBase):
    pass

class ProjectDocumentResponse(ProjectDocumentBase):
    id: uuid.UUID
    project_id: uuid.UUID
    uploaded_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Project Funding Schemas
class ProjectFundingBase(BaseModel):
    round_type: str
    amount: float
    currency: str = "USD"
    date: datetime
    investors: Optional[List[Dict[str, Any]]] = None

class ProjectFundingCreate(ProjectFundingBase):
    pass

class ProjectFundingResponse(ProjectFundingBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Graph Stakeholder Schema
class StakeholderResponse(BaseModel):
    user_id: uuid.UUID
    name: str
    email: str
    avatar_url: Optional[str] = None
    role: str # mentors, advises, invests_in

class IncubationDashboardResponse(BaseModel):
    project_id: uuid.UUID
    updates: List[ProjectUpdateResponse]
    documents: List[ProjectDocumentResponse]
    funding_rounds: List[ProjectFundingResponse]
    stakeholders: List[StakeholderResponse]
