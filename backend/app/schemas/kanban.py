from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class KanbanTaskLabelBase(BaseModel):
    name: str
    color: str

class KanbanTaskLabelResponse(KanbanTaskLabelBase):
    id: uuid.UUID
    board_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class KanbanTaskBase(BaseModel):
    title: str
    description: str | None = None

class KanbanTaskCreate(KanbanTaskBase):
    pass

class KanbanTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    column_id: uuid.UUID | None = None
    position: float | None = None

class KanbanTaskResponse(KanbanTaskBase):
    id: uuid.UUID
    column_id: uuid.UUID
    position: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class KanbanColumnBase(BaseModel):
    name: str

class KanbanColumnCreate(KanbanColumnBase):
    pass

class KanbanColumnUpdate(BaseModel):
    name: str | None = None
    position: float | None = None

class KanbanColumnResponse(KanbanColumnBase):
    id: uuid.UUID
    board_id: uuid.UUID
    position: float
    tasks: list[KanbanTaskResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class KanbanBoardResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    columns: list[KanbanColumnResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
