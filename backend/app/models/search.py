import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseEntity

class ContentEmbedding(BaseEntity):
    __tablename__ = "content_embeddings"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Store embedding as a JSON list of floats for sqlite compatibility
    # In a production PostgreSQL environment, this would use pgvector's Vector type
    embedding = Column(JSON, nullable=False)
    
    content_hash = Column(String, nullable=False)
    
    # Track the model used to generate this embedding (e.g. text-embedding-004)
    model_version = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
