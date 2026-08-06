from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class HackathonRoundExport(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class HackathonRequirementExport(BaseModel):
    title: str
    description: Optional[str] = None
    is_required: bool = True

class HackathonExport(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    timezone: str = "UTC"
    theme: Optional[str] = None
    
    rounds: List[HackathonRoundExport] = Field(default_factory=list)
    requirements: List[HackathonRequirementExport] = Field(default_factory=list)

class HackathonImportRequest(BaseModel):
    data: HackathonExport
    workspace_id: str
    overwrite_existing: bool = False
