from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.kanban import (
    KanbanBoardResponse, KanbanColumnCreate, KanbanColumnResponse, KanbanColumnUpdate,
    KanbanTaskCreate, KanbanTaskResponse, KanbanTaskUpdate
)
from app.services import kanban_service

router = APIRouter()

@router.get("/workspaces/{workspace_id}/projects/{project_id}/kanban", response_model=KanbanBoardResponse)
async def get_kanban_board(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await kanban_service.get_board_by_project(db, workspace_id, project_id)

@router.post("/workspaces/{workspace_id}/kanban/boards/{board_id}/columns", response_model=KanbanColumnResponse)
async def create_kanban_column(
    workspace_id: uuid.UUID,
    board_id: uuid.UUID,
    column_in: KanbanColumnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await kanban_service.create_column(db, workspace_id, board_id, column_in, current_user)

@router.patch("/workspaces/{workspace_id}/kanban/columns/{column_id}", response_model=KanbanColumnResponse)
async def update_kanban_column(
    workspace_id: uuid.UUID,
    column_id: uuid.UUID,
    column_in: KanbanColumnUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await kanban_service.update_column(db, column_id, column_in, current_user)

@router.post("/workspaces/{workspace_id}/kanban/columns/{column_id}/tasks", response_model=KanbanTaskResponse)
async def create_kanban_task(
    workspace_id: uuid.UUID,
    column_id: uuid.UUID,
    task_in: KanbanTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await kanban_service.create_task(db, workspace_id, column_id, task_in, current_user)

@router.patch("/workspaces/{workspace_id}/kanban/tasks/{task_id}", response_model=KanbanTaskResponse)
async def update_kanban_task(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    task_in: KanbanTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await kanban_service.update_task(db, task_id, task_in, current_user)
