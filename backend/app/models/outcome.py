import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseEntity
import enum

class ResultType(str, enum.Enum):
    winner = "winner"
    runner_up = "runner_up"
    honorable_mention = "honorable_mention"
    category_winner = "category_winner"
    participant = "participant"

class ResultStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class RewardType(str, enum.Enum):
    cash = "cash"
    swag = "swag"
    credit = "credit"
    hardware = "hardware"
    certificate = "certificate"
    other = "other"

class RewardStatus(str, enum.Enum):
    pending = "pending"
    fulfilled = "fulfilled"
    forfeited = "forfeited"

class AchievementType(str, enum.Enum):
    medal = "medal"
    badge = "badge"
    certificate = "certificate"
    milestone = "milestone"

class HackathonResult(BaseEntity):
    __tablename__ = "hackathon_results"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_rounds.id", ondelete="SET NULL"), nullable=True, index=True)
    result_type = Column(Enum(ResultType, name="result_type_enum"), default=ResultType.participant, nullable=False)
    position = Column(Integer, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(ResultStatus, name="result_status_enum"), default=ResultStatus.draft, nullable=False)
    announced_at = Column(DateTime(timezone=True), nullable=True)
    source_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_note = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class Reward(BaseEntity):
    __tablename__ = "rewards"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=True, index=True)
    result_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_results.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String, nullable=False)
    reward_type = Column(Enum(RewardType, name="reward_type_enum"), default=RewardType.other, nullable=False)
    monetary_value = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)
    sponsor = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(Enum(RewardStatus, name="reward_status_enum"), default=RewardStatus.pending, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class Achievement(BaseEntity):
    __tablename__ = "achievements"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=True, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    result_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_results.id", ondelete="SET NULL"), nullable=True, index=True)
    achievement_type = Column(Enum(AchievementType, name="achievement_type_enum"), default=AchievementType.badge, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    achieved_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    visibility = Column(String, default="public")
    source = Column(String, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
