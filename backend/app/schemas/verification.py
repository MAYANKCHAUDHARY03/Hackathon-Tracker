from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class VerificationCreate(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    achievement_type: str
    achievement_detail: Optional[str] = None
    source: str
    
class VerificationResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    achievement_type: str
    achievement_detail: Optional[str] = None
    status: str
    source: str
    verifier_id: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
