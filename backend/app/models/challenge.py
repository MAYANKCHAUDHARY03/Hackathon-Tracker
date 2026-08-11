import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class Challenge(BaseEntity):
    __tablename__ = "challenges"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("hackathons.id", ondelete="SET NULL"), nullable=True, index=True)
    problem_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("problems.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    category: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    domain: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    difficulty: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    visibility: Mapped[str] = mapped_column(String, default="public", index=True) # public, internal
    submission_count: Mapped[int] = mapped_column(default=0)
    
    status: Mapped[str] = mapped_column(String, default="active", index=True)
    
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace = relationship("Workspace")
    hackathon = relationship("Hackathon")
    problem = relationship("Problem")
