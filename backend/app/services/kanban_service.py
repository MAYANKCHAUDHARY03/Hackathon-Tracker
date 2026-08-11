import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.kanban import KanbanBoard, KanbanColumn, Task
from app.schemas.kanban import KanbanTaskCreate, KanbanTaskUpdate, KanbanColumnCreate, KanbanColumnUpdate
from app.models.user import User
from app.services import activity_service

async def get_board_by_project(db: AsyncSession, workspace_id: uuid.UUID, project_id: uuid.UUID):
    stmt = (
        select(KanbanBoard)
        .where(
            KanbanBoard.workspace_id == workspace_id,
            KanbanBoard.project_id == project_id
        )
        .options(
            selectinload(KanbanBoard.columns).selectinload(KanbanColumn.tasks)
        )
    )
    result = await db.execute(stmt)
    board = result.scalars().first()
    
    if not board:
        raise HTTPException(status_code=404, detail="Kanban board not found for this project")
        
    board.columns.sort(key=lambda c: c.position)
    for col in board.columns:
        col.tasks.sort(key=lambda t: t.position)
        
    return board

async def get_board_for_column(db: AsyncSession, column_id: uuid.UUID):
    stmt = select(KanbanColumn).where(KanbanColumn.id == column_id).options(selectinload(KanbanColumn.board))
    result = await db.execute(stmt)
    col = result.scalars().first()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    return col.board

async def create_column(db: AsyncSession, workspace_id: uuid.UUID, board_id: uuid.UUID, column_in: KanbanColumnCreate, user: User):
    stmt = select(KanbanColumn.position).where(KanbanColumn.board_id == board_id).order_by(KanbanColumn.position.desc()).limit(1)
    result = await db.execute(stmt)
    max_pos = result.scalars().first()
    next_pos = (max_pos or 0) + 1000.0

    column = KanbanColumn(
        workspace_id=workspace_id,
        board_id=board_id,
        name=column_in.name,
        position=next_pos
    )
    db.add(column)
    
    # get board to find project_id
    board_stmt = select(KanbanBoard).where(KanbanBoard.id == board_id)
    board = (await db.execute(board_stmt)).scalars().first()
    
    await activity_service.log_activity(
        db, workspace_id, user.id, "created", "KanbanColumn", column.id, board.project_id, {"name": column.name}
    )
    
    await db.commit()
    await db.refresh(column)
    return column

async def update_column(db: AsyncSession, column_id: uuid.UUID, column_in: KanbanColumnUpdate, user: User):
    stmt = select(KanbanColumn).where(KanbanColumn.id == column_id).options(selectinload(KanbanColumn.board))
    result = await db.execute(stmt)
    column = result.scalars().first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
        
    edge_metadata = {}
    if column_in.name is not None and column_in.name != column.name:
        edge_metadata["old_name"] = column.name
        edge_metadata["new_name"] = column_in.name
        column.name = column_in.name
    if column_in.position is not None:
        column.position = column_in.position
        
    await activity_service.log_activity(
        db, column.workspace_id, user.id, "updated", "KanbanColumn", column.id, column.board.project_id, edge_metadata
    )
        
    await db.commit()
    await db.refresh(column)
    return column

async def create_task(db: AsyncSession, workspace_id: uuid.UUID, column_id: uuid.UUID, task_in: KanbanTaskCreate, user: User):
    board = await get_board_for_column(db, column_id)
    
    stmt = select(Task.position).where(Task.column_id == column_id).order_by(Task.position.desc()).limit(1)
    result = await db.execute(stmt)
    max_pos = result.scalars().first()
    next_pos = (max_pos or 0) + 1000.0

    task = Task(
        workspace_id=workspace_id,
        column_id=column_id,
        title=task_in.title,
        description=task_in.description,
        position=next_pos
    )
    db.add(task)
    
    await activity_service.log_activity(
        db, workspace_id, user.id, "created", "KanbanTask", task.id, board.project_id, {"title": task.title}
    )
    
    await db.commit()
    await db.refresh(task)
    return task

async def update_task(db: AsyncSession, task_id: uuid.UUID, task_in: KanbanTaskUpdate, user: User):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    board = await get_board_for_column(db, task.column_id)

    edge_metadata = {}
    if task_in.title is not None and task_in.title != task.title:
        edge_metadata["old_title"] = task.title
        edge_metadata["new_title"] = task_in.title
        task.title = task_in.title
        
    if task_in.description is not None:
        task.description = task_in.description
        
    action = "updated"
    if task_in.column_id is not None and task_in.column_id != task.column_id:
        action = "moved"
        edge_metadata["old_column_id"] = str(task.column_id)
        edge_metadata["new_column_id"] = str(task_in.column_id)
        task.column_id = task_in.column_id
        
    if task_in.position is not None:
        task.position = task_in.position

    await activity_service.log_activity(
        db, task.workspace_id, user.id, action, "KanbanTask", task.id, board.project_id, edge_metadata
    )

    await db.commit()
    await db.refresh(task)
    return task
