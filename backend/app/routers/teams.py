from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.team import TeamResponse, TeamCreate
from app.services import team_service

router = APIRouter()

@router.get("/workspaces/{workspace_id}/teams", response_model=list[TeamResponse])
async def get_teams(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await team_service.get_teams(db, workspace_id)

@router.post("/workspaces/{workspace_id}/teams", response_model=TeamResponse)
async def create_team(
    workspace_id: uuid.UUID,
    team_in: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await team_service.create_team(db, workspace_id, team_in.hackathon_id, team_in, current_user)
