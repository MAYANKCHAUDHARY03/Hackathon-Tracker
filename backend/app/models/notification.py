import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import BaseEntity
import enum

class NotificationCategory(str, enum.Enum):
    deadline = "deadline"
    task = "task"
    round = "round"
    submission = "submission"
    team = "team"
    project = "project"
    evaluation = "evaluation"
    result = "result"
    reward = "reward"
    system = "system"

class NotificationSeverity(str, enum.Enum):
    info = "info"
    success = "success"
    warning = "warning"
    urgent = "urgent"

def utc_now():
    return datetime.now(timezone.utc)

class Notification(BaseEntity):
    __tablename__ = "notifications"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type = Column(String, nullable=False)
    category = Column(Enum(NotificationCategory, name="notification_category_enum"), nullable=False)
    severity = Column(Enum(NotificationSeverity, name="notification_severity_enum"), default=NotificationSeverity.info, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    action_url = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    event_key = Column(String, nullable=True, unique=True, index=True)
    safe_edge_metadata = Column(JSON, nullable=True)
    occurred_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

class NotificationPreference(BaseEntity):
    __tablename__ = "notification_preferences"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(Enum(NotificationCategory, name="notification_category_enum_pref"), nullable=False)
    in_app_enabled = Column(Boolean, default=True)
    reminder_offsets = Column(JSON, nullable=True) # list of minutes (e.g. [1440, 360, 60])
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String, nullable=True) # e.g. "22:00"
    quiet_hours_end = Column(String, nullable=True) # e.g. "08:00"
    timezone = Column(String, default="UTC")

