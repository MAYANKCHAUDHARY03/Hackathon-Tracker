import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, JSON, DateTime, Index, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity


class EdgeProvenance(str, enum.Enum):
    """How this edge was created — determines trust level."""
    verified = "verified"            # From platform actions or human verification
    user_provided = "user-provided"  # Explicitly created by a user
    imported = "imported"            # From external data import
    ai_inferred = "AI-inferred"      # Suggested by AI — requires user acceptance


# Canonical relationship types for the Innovation Knowledge Graph
RELATION_TYPES = {
    # Structural (auto-created from model events)
    "contains",         # Hackathon → Team, Hackathon → Challenge
    "belongs_to",       # Workspace → Organization
    "created",          # Team → Project
    "member_of",        # User → Team

    # User-provided
    "solves",           # Project → Challenge
    "uses",             # Project → Technology
    "mentored_by",      # Team → Person
    "evaluated_by",     # Project → Person
    "participated_in",  # User → Hackathon
    "created_by",       # Project → User, Challenge → User
    "inspired_by",      # Project → Project
    "evolved_from",     # Startup → Project
    "deployed_at",      # Project → Organization
    "sponsored_by",     # Hackathon → Sponsor
    "organized_by",     # Hackathon → Organization

    # Research (Phase 31)
    "cites",            # Project → ResearchLink
    "uses_dataset",     # Project → ResearchLink

    # AI-inferred
    "similar_to",       # Project → Project
    "related_to",       # Challenge → Challenge
    "expert_in",        # User → Technology
    "potential_mentor",  # Person → Challenge
}


class GraphEdge(BaseEntity):
    __tablename__ = "graph_edges"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )

    source_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)

    target_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)

    relation_type: Mapped[str] = mapped_column(String, index=True, nullable=False)

    # Phase 28: Provenance & Trust
    provenance: Mapped[str] = mapped_column(
        String, nullable=False, default=EdgeProvenance.user_provided.value, index=True
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0
    )

    # Who created this edge
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Verification tracking
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Edge-specific properties (e.g., role, weight, label)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)

    # Additional context (AI model info, import source, timestamps)
    edge_edge_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_graph_edges_source", "source_type", "source_id"),
        Index("ix_graph_edges_target", "target_type", "target_id"),
        Index("ix_graph_edges_relation", "source_id", "relation_type", "target_id", unique=True),
        Index("ix_graph_edges_workspace_relation", "workspace_id", "relation_type"),
        Index("ix_graph_edges_provenance", "workspace_id", "provenance"),
    )

    # Relationships for creator/verifier
    creator = relationship("User", foreign_keys=[created_by])
    verifier = relationship("User", foreign_keys=[verified_by])
