import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class Problem(BaseEntity):
    __tablename__ = "problems"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, index=True, unique=True)
    description: Mapped[str] = mapped_column(Text)
    
    domain: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    impact_potential: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="open", index=True) # open, validating, active, solved, archived
    
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace = relationship("Workspace")
    creator = relationship("User")
    
    # Relationships
    # challenges = relationship("Challenge", back_populates="problem")
