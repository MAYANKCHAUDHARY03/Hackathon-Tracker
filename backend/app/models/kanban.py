from enum import Enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseEntity

class ColumnSemanticType(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class KanbanBoard(BaseEntity):
    __tablename__ = "kanban_boards"

    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False, default="Project Board")

    project = relationship("Project", backref="board", uselist=False)
    columns = relationship("KanbanColumn", back_populates="board", cascade="all, delete-orphan", order_by="KanbanColumn.position")
    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")
    labels = relationship("TaskLabel", back_populates="board", cascade="all, delete-orphan")


class KanbanColumn(BaseEntity):
    __tablename__ = "kanban_columns"

    board_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_boards.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    semantic_type: Mapped[str] = mapped_column(String, nullable=False, default=ColumnSemanticType.TODO.value)
    position: Mapped[float] = mapped_column(Float, nullable=False)
    wip_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)

    board = relationship("KanbanBoard", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan", order_by="Task.position")


class Task(BaseEntity):
    __tablename__ = "kanban_tasks"

    board_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_boards.id", ondelete="CASCADE"), nullable=False)
    column_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_columns.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String, nullable=False, default=TaskPriority.MEDIUM.value)
    position: Mapped[float] = mapped_column(Float, nullable=False)
    
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_milestone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    board = relationship("KanbanBoard", back_populates="tasks")
    column = relationship("KanbanColumn", back_populates="tasks")
    assignees = relationship("TaskAssignee", back_populates="task", cascade="all, delete-orphan")
    label_assignments = relationship("TaskLabelAssignment", back_populates="task", cascade="all, delete-orphan")


class TaskAssignee(BaseEntity):
    __tablename__ = "kanban_task_assignees"
    __table_args__ = (UniqueConstraint('task_id', 'user_id', name='uq_task_assignee'),)

    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_tasks.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    task = relationship("Task", back_populates="assignees")
    user = relationship("User")


class TaskLabel(BaseEntity):
    __tablename__ = "kanban_task_labels"
    __table_args__ = (UniqueConstraint('board_id', 'name', name='uq_board_label_name'),)

    board_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_boards.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False, default="#808080")

    board = relationship("KanbanBoard", back_populates="labels")
    assignments = relationship("TaskLabelAssignment", back_populates="label", cascade="all, delete-orphan")


class TaskLabelAssignment(BaseEntity):
    __tablename__ = "kanban_task_label_assignments"
    __table_args__ = (UniqueConstraint('task_id', 'label_id', name='uq_task_label'),)

    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_tasks.id", ondelete="CASCADE"), nullable=False)
    label_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kanban_task_labels.id", ondelete="CASCADE"), nullable=False)

    task = relationship("Task", back_populates="label_assignments")
    label = relationship("TaskLabel", back_populates="assignments")
