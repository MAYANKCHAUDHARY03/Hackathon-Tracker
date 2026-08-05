import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class HackathonRound(BaseEntity):
    __tablename__ = "hackathon_rounds"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    round_type: Mapped[str] = mapped_column(String, nullable=False) # registration, idea_submission, etc
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, default="upcoming", index=True)
    
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("hackathon_id", "sequence", name="uq_round_sequence_per_hackathon"),
    )

    hackathon = relationship("Hackathon", backref="rounds")


class Deadline(BaseEntity):
    __tablename__ = "deadlines"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    round_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("hackathon_rounds.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline_type: Mapped[str] = mapped_column(String, nullable=False)
    
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_hard_deadline: Mapped[bool] = mapped_column(Boolean, default=False)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    round = relationship("HackathonRound", backref="deadlines")
    hackathon = relationship("Hackathon", backref="deadlines")


class RoundProgress(BaseEntity):
    __tablename__ = "round_progress"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    round_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathon_rounds.id", ondelete="CASCADE"), index=True)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    
    status: Mapped[str] = mapped_column(String, default="not_started", index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("team_id", "round_id", name="uq_team_progress_per_round"),
    )

    round = relationship("HackathonRound", backref="team_progress")
    team = relationship("Team", backref="round_progress")
