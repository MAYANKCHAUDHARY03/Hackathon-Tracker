import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseEntity
import enum

class PersonVisibility(str, enum.Enum):
    workspace = "workspace"
    team = "team"
    private = "private"

class MentorStatus(str, enum.Enum):
    planned = "planned"
    completed = "completed"
    cancelled = "cancelled"
    archived = "archived"

class Person(BaseEntity):
    __tablename__ = "people"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String, nullable=False)
    organisation = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    expertise_areas = Column(JSON, nullable=True)
    bio = Column(String, nullable=True)
    public_profile_url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    visibility = Column(Enum(PersonVisibility, name="person_visibility_enum"), default=PersonVisibility.workspace)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class MentorAssignment(BaseEntity):
    __tablename__ = "mentor_assignments"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_rounds.id", ondelete="SET NULL"), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String, nullable=True)
    session_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    status = Column(Enum(MentorStatus, name="mentor_status_enum"), default=MentorStatus.planned)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class JudgeAssignment(BaseEntity):
    __tablename__ = "judge_assignments"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_rounds.id", ondelete="SET NULL"), nullable=True, index=True)
    judge_id = Column(UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=True)
    panel_name = Column(String, nullable=True)
    assignment_notes = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
