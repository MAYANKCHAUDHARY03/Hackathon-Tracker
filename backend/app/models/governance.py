from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
import enum
from typing import Dict, Any
import uuid

from app.models.base import Base, BaseEntity

class DSRType(str, enum.Enum):
    EXPORT = "export"
    DELETION = "deletion"
    RECTIFICATION = "rectification"

class DSRStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class DataSubjectRequest(BaseEntity):
    __tablename__ = "data_subject_requests"

    # id, created_at, updated_at inherited from BaseEntity
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    request_type = Column(SQLEnum(DSRType), nullable=False)
    status = Column(SQLEnum(DSRStatus), default=DSRStatus.PENDING, nullable=False)
    details = Column(Text, nullable=True) # E.g., which data to rectify
    resolution_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class ConsentRecord(BaseEntity):
    __tablename__ = "consent_records"

    # id, created_at, updated_at inherited from BaseEntity
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    consent_type = Column(String(100), nullable=False) # e.g. "marketing_emails", "data_sharing"
    status = Column(String(50), nullable=False) # e.g. "granted", "revoked"
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

class GovernanceAuditLog(BaseEntity):
    __tablename__ = "governance_audit_logs"

    # id, created_at, updated_at inherited from BaseEntity
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    target_resource = Column(String(255), nullable=True)
    target_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
