import enum
import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseEntity
from app.models.portable_identity import VisibilityTier

class ProjectStage(str, enum.Enum):
    HACKATHON = "hackathon"
    PROTOTYPE = "prototype"
    INCUBATION = "incubation"
    PILOT = "pilot"
    STARTUP = "startup"
    PRODUCTION = "production"

class PortableProjectIdentity(BaseEntity):
    __tablename__ = "portable_project_identities"

    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    current_stage: Mapped[ProjectStage] = mapped_column(Enum(ProjectStage), default=ProjectStage.HACKATHON)
    
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    visibility: Mapped[VisibilityTier] = mapped_column(Enum(VisibilityTier), default=VisibilityTier.PRIVATE)

    # Relationship to tracking transitions
    transitions = relationship("ProjectStageTransition", back_populates="portable_project", cascade="all, delete-orphan", order_by="ProjectStageTransition.transition_date")
    owner = relationship("User")


class ProjectStageTransition(BaseEntity):
    __tablename__ = "project_stage_transitions"
    
    portable_project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portable_project_identities.id", ondelete="CASCADE"), index=True)
    
    from_stage: Mapped[ProjectStage | None] = mapped_column(Enum(ProjectStage), nullable=True)
    to_stage: Mapped[ProjectStage] = mapped_column(Enum(ProjectStage))
    
    transition_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Traceability Context
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    program_context_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    program_context_type: Mapped[str | None] = mapped_column(String, nullable=True)
    
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    portable_project = relationship("PortableProjectIdentity", back_populates="transitions")
