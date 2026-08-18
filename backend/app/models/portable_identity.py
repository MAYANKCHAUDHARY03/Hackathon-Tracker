import uuid
from sqlalchemy import String, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import BaseEntity

class VisibilityTier(str, enum.Enum):
    PRIVATE = "private"
    CONNECTION_ONLY = "connection_only"
    SELECTIVE_SHARING = "selective_sharing"
    PUBLIC = "public"

class PortableIdentity(BaseEntity):
    __tablename__ = "portable_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Global innovation metrics
    total_projects: Mapped[int] = mapped_column(default=0)
    total_achievements: Mapped[int] = mapped_column(default=0)
    
    # Granular visibility controls
    visibility_projects: Mapped[VisibilityTier] = mapped_column(Enum(VisibilityTier), default=VisibilityTier.PRIVATE)
    visibility_achievements: Mapped[VisibilityTier] = mapped_column(Enum(VisibilityTier), default=VisibilityTier.PRIVATE)
    visibility_skills: Mapped[VisibilityTier] = mapped_column(Enum(VisibilityTier), default=VisibilityTier.PRIVATE)
    
    # Which specific workspaces are allowed in Selective Sharing
    selective_sharing_workspaces: Mapped[list] = mapped_column(JSON, default=list) # List of workspace UUIDs

class VerifiedSkill(BaseEntity):
    __tablename__ = "verified_skills"
    
    identity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portable_identities.id", ondelete="CASCADE"), index=True)
    skill_name: Mapped[str]
    verification_level: Mapped[str] = mapped_column(default="Self-Declared") # Unverified, Self-Declared, Platform-Verified, Organization-Verified, Multi-Source Verified
    evidence_trail: Mapped[list] = mapped_column(JSON, default=list) # e.g. [{"source": "Hackathon X", "type": "submission", "url": "..."}]
