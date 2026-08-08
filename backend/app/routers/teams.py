from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.team import TeamResponse, TeamCreate, TeamUpdate
from app.services import team_service
from app.services.match_service import MatchService

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

@router.patch("/workspaces/{workspace_id}/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    team_in: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await team_service.update_team(db, workspace_id, team_id, team_in, current_user)

@router.get("/workspaces/{workspace_id}/teams/{team_id}/talent-matches")
async def get_talent_matches(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await MatchService.evaluate_talent_matches(db, workspace_id, team_id)

@router.post("/workspaces/{workspace_id}/teams/{team_id}/apply")
async def apply_to_team(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await MatchService.apply_to_team(db, workspace_id, team_id, current_user)

@router.post("/workspaces/{workspace_id}/teams/{team_id}/invite/{person_id}")
async def invite_to_team(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await MatchService.invite_to_team(db, workspace_id, team_id, person_id, current_user)
