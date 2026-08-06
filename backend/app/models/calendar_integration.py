from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseEntity

class CalendarIntegration(BaseEntity):
    __tablename__ = "calendar_integrations"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False) # 'google' or 'outlook'
    remote_calendar_id = Column(String(255), nullable=True) # e.g. the calendar ID in google where events are pushed
    
    # OAuth Tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)

    # Relationships
    workspace = relationship("Workspace")
