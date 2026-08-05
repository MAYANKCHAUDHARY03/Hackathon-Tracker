import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class Team(BaseEntity):
    __tablename__ = "teams"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", index=True)
    
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("hackathon_id", "name", name="uq_team_name_per_hackathon"),
        UniqueConstraint("hackathon_id", "slug", name="uq_team_slug_per_hackathon"),
    )

    workspace = relationship("Workspace")
    hackathon = relationship("Hackathon")
    creator = relationship("User")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(BaseEntity):
    __tablename__ = "team_members"

    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    authorization_role: Mapped[str] = mapped_column(String, default="member") # lead, co_lead, member
    specialty: Mapped[str | None] = mapped_column(String, nullable=True)
    custom_specialty: Mapped[str | None] = mapped_column(String, nullable=True)
    
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    team = relationship("Team", back_populates="members")
    user = relationship("User")
