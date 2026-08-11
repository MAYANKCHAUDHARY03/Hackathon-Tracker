from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class NotificationPreferenceBase(BaseModel):
    category: str
    in_app_enabled: bool = True
    reminder_offsets: list[int] | None = None
    quiet_hours_enabled: bool = False
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    timezone: str = "UTC"

class NotificationPreferenceCreate(NotificationPreferenceBase):
    pass

class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool | None = None
    reminder_offsets: list[int] | None = None
    quiet_hours_enabled: bool | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    timezone: str | None = None

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: UUID
    workspace_id: UUID | None = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationBase(BaseModel):
    notification_type: str
    category: str
    severity: str
    title: str
    body: str | None = None
    action_url: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    event_key: str | None = None
    safe_edge_metadata: dict | None = None
    occurred_at: datetime
    expires_at: datetime | None = None

class NotificationResponse(NotificationBase):
    id: UUID
    workspace_id: UUID
    recipient_user_id: UUID
    read_at: datetime | None = None
    dismissed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int

class NotificationSummaryResponse(BaseModel):
    total_unread: int
    unread_by_category: dict[str, int]
    total: int
