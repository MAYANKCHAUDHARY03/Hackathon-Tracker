from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime

class ApplicationFormBase(BaseModel):
    title: str
    description: Optional[str] = None
    schema_json: Dict[str, Any]
    is_published: Optional[bool] = False

class ApplicationFormCreate(ApplicationFormBase):
    pass

class ApplicationFormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    schema_json: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None

class ApplicationForm(ApplicationFormBase):
    id: str
    hackathon_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ApplicationSubmissionBase(BaseModel):
    data_json: Dict[str, Any]

class ApplicationSubmissionCreate(ApplicationSubmissionBase):
    pass

class ApplicationSubmissionUpdateStatus(BaseModel):
    status: str

class ApplicationSubmission(ApplicationSubmissionBase):
    id: str
    form_id: str
    user_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
