import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Text, DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity
from app.models.workspace import Workspace

class Hackathon(BaseEntity):
    __tablename__ = "hackathons"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(Text)
    organiser: Mapped[str | None]
    official_url: Mapped[str | None]
    mode: Mapped[str] = mapped_column(String, default="online")
    location: Mapped[str | None]
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    timezone: Mapped[str] = mapped_column(String, nullable=False, default="UTC")
    max_team_size: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String, default="draft", index=True)
    program_type: Mapped[str] = mapped_column(String, default="hackathon", index=True)
    teams = relationship("Team", back_populates="hackathon", cascade="all, delete-orphan")
    application_forms = relationship("ApplicationForm", back_populates="hackathon", cascade="all, delete-orphan")
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    workspace = relationship("Workspace")
