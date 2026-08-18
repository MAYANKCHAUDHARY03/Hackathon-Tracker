import uuid
import enum
from sqlalchemy import Column, String, JSON, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import BaseEntity

class MemoryType(str, enum.Enum):
    CONVERSATION = "conversation"
    TASK = "task"
    ORGANIZATION = "organization"

class AgentMemory(BaseEntity):
    __tablename__ = "agent_memories"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    memory_type = Column(SQLEnum(MemoryType), nullable=False, index=True)
    
    content = Column(JSON, nullable=False)
    
    # Optional metadata for provenance, e.g. from which entity or task it was derived
    source_id = Column(String(255), nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        # using naive UTC here for simplicity, assuming app uses timezone-aware or utcnow everywhere
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)
