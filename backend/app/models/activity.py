import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON

from app.models.base import BaseEntity

class ActivityEvent(BaseEntity):
    __tablename__ = "activity_events"

    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    board_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_boards.id", ondelete="CASCADE"), nullable=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    entity_type: Mapped[str] = mapped_column(String, nullable=False) # e.g., 'task', 'board', 'column'
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    action: Mapped[str] = mapped_column(String, nullable=False) # e.g., 'created', 'updated', 'moved'
    safe_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True) # E.g. {"old_column": "Todo", "new_column": "Done", "task_title": "Fix bug"}

    workspace = relationship("Workspace")
    project = relationship("Project")
    board = relationship("KanbanBoard")
    actor = relationship("User")
