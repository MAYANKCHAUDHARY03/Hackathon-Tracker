import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class PlatformEvent(Base):
    __tablename__ = "platform_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=True, index=True)
    
    event_type = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False, default="api")
    correlation_id = Column(String(100), nullable=True, index=True)
    
    metadata_json = Column(JSON, nullable=True, default=dict)
