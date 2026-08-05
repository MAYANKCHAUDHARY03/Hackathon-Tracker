from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.project import ProjectResponse, ProjectCreate
from app.services import project_service

router = APIRouter()

@router.get("/workspaces/{workspace_id}/projects", response_model=list[ProjectResponse])
async def get_projects(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.get_projects(db, workspace_id)

@router.post("/workspaces/{workspace_id}/teams/{team_id}/projects", response_model=ProjectResponse)
async def create_project(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.create_project(db, workspace_id, team_id, project_in, current_user)
