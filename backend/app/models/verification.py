import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class TrustVerification(BaseEntity):
    __tablename__ = "trust_verifications"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[str] = mapped_column(String, index=True) # e.g. "user", "project"
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    
    achievement_type: Mapped[str] = mapped_column(String) # e.g., "award", "skill"
    achievement_detail: Mapped[str | None] = mapped_column(String, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    source: Mapped[str] = mapped_column(String)
    
    verifier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    workspace = relationship("Workspace")
    verifier = relationship("User")
