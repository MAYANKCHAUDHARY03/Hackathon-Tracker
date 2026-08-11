import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class ResearchLink(BaseEntity):
    __tablename__ = "research_links"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    
    type: Mapped[str] = mapped_column(String(50), index=True) # paper, patent, dataset, repo, institution, other
    title: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    identifier: Mapped[str | None] = mapped_column(String, nullable=True, index=True) # DOI, Patent number, etc.
    
    authors: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    publication_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # provenance: user-provided, verified, inferred
    provenance: Mapped[str] = mapped_column(String(50), default="user-provided", index=True)
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    project = relationship("Project")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
