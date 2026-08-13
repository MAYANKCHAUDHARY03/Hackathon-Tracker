import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.models.base import Base

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AgentApprovalRequest(Base):
    __tablename__ = "agent_approval_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    agent_name = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    parameters_json = Column(JSON, nullable=False, default=dict)
    risk_level = Column(String, nullable=False)
    
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    
    justification = Column(String, nullable=True)
    
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
