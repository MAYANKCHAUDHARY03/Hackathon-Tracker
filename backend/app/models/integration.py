from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

from app.models.base import BaseEntity

class ExternalSubmissionConnection(BaseEntity):
    """
    Represents a connection to an external submission provider (e.g. Devfolio, Unstop).
    """
    __tablename__ = "external_submission_connections"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False) # devfolio, unstop, hackerearth
    
    # Store credentials securely or just API keys
    credentials: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Optional relationships
    workspace = relationship("Workspace", backref="external_connections")


class ExternalSubmissionMapping(BaseEntity):
    """
    Maps an internal submission to an external provider's submission record.
    """
    __tablename__ = "external_submission_mappings"
    
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("round_submissions.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("external_submission_connections.id", ondelete="CASCADE"), nullable=False)
    
    external_reference_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_status: Mapped[str] = mapped_column(String(50), nullable=True)
    
    sync_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    submission = relationship("RoundSubmission", backref="external_mappings")
    connection = relationship("ExternalSubmissionConnection")
