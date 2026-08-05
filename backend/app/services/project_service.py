import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.models.user import User
from app.models.kanban import KanbanBoard, KanbanColumn

async def get_projects(db: AsyncSession, workspace_id: uuid.UUID):
    stmt = select(Project).where(Project.workspace_id == workspace_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_project(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID, project_in: ProjectCreate, user: User):
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', project_in.name.lower()).strip('-')
    project = Project(
        workspace_id=workspace_id,
        team_id=team_id,
        title=project_in.name,
        slug=slug,
        description=project_in.description,
        repository_url=project_in.repository_url,
        hackathon_id=project_in.hackathon_id
    )
    db.add(project)
    
    # We must explicitly flush so the project gets an ID before we can create a board
    await db.flush()

    # Automatically create a KanbanBoard for the new Project
    board = KanbanBoard(
        workspace_id=workspace_id,
        project_id=project.id,
        name=f"{project.title} Board"
    )
    db.add(board)
    await db.flush()

    # Create default columns
    default_columns = [
        ("Todo", 1000.0),
        ("In Progress", 2000.0),
        ("Done", 3000.0)
    ]
    for name, pos in default_columns:
        col = KanbanColumn(
            board_id=board.id,
            name=name,
            position=pos
        )
        db.add(col)

    await db.commit()
    await db.refresh(project)
    return project
