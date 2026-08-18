from typing import Any, Dict, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.memory import MemoryType

class AgentMemoryBase(BaseModel):
    agent_name: str
    memory_type: MemoryType
    content: Dict[str, Any]
    source_id: Optional[str] = None
    expires_at: Optional[datetime] = None

class AgentMemoryCreate(AgentMemoryBase):
    pass

class AgentMemoryResponse(AgentMemoryBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
