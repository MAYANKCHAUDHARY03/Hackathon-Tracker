import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class SubmissionRequirement(BaseEntity):
    __tablename__ = "submission_requirements"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    round_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathon_rounds.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirement_type: Mapped[str] = mapped_column(String, nullable=False) # e.g. 'url', 'github_url', 'video_url', 'text'
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Validation rules stored in JSON, e.g. min/max length, required domains for URLs
    validation_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("round_id", "sequence", name="uq_requirement_sequence_per_round"),
    )
    
    round = relationship("HackathonRound", backref="requirements")


class RoundSubmission(BaseEntity):
    __tablename__ = "round_submissions"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    round_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathon_rounds.id", ondelete="CASCADE"), index=True)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    
    status: Mapped[str] = mapped_column(String, default="draft", index=True) # draft, submitted, locked
    
    # Store a point-in-time snapshot of the submission at the exact moment it was submitted
    snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("team_id", "round_id", name="uq_team_submission_per_round"),
    )
    
    round = relationship("HackathonRound", backref="submissions")
    team = relationship("Team", backref="submissions")


class SubmissionItem(BaseEntity):
    __tablename__ = "submission_items"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("round_submissions.id", ondelete="CASCADE"), index=True)
    requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submission_requirements.id", ondelete="CASCADE"), index=True)
    
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # To determine if the specific item meets requirements independently
    is_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("submission_id", "requirement_id", name="uq_submission_item_per_requirement"),
    )
    
    submission = relationship("RoundSubmission", backref="items")
    requirement = relationship("SubmissionRequirement", backref="items")
