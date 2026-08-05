from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.activity import ActivityEventResponse
from app.services import activity_service

router = APIRouter()

@router.get("/workspaces/{workspace_id}/projects/{project_id}/activities", response_model=list[ActivityEventResponse])
async def get_activities(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await activity_service.get_project_activities(db, workspace_id, project_id)
