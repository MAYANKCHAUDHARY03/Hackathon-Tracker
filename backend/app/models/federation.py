import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.models.base import BaseEntity

class FederationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVOKED = "revoked"

class WorkspaceFederation(BaseEntity):
    __tablename__ = "workspace_federations"

    source_workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    target_workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    
    status: Mapped[FederationStatus] = mapped_column(
        Enum(FederationStatus), default=FederationStatus.PENDING
    )
    
    shared_entities: Mapped[list] = mapped_column(JSON, default=list) # e.g. ["challenges", "mentors"]

    __table_args__ = (
        Index("ix_federation_link", "source_workspace_id", "target_workspace_id", unique=True),
    )
