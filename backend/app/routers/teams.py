from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User, WorkspaceMembership
from app.dependencies import get_current_user, verify_workspace_access, require_team_lead_or_colead
from app.schemas.team import TeamResponse, TeamCreate, TeamUpdate
from app.services import team_service
from app.services.match_service import MatchService

router = APIRouter()

@router.get("/workspaces/{workspace_id}/teams", response_model=list[TeamResponse])
async def get_teams(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await team_service.get_teams(db, workspace_id)

@router.post("/workspaces/{workspace_id}/teams", response_model=TeamResponse)
async def create_team(
    workspace_id: uuid.UUID,
    team_in: TeamCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await team_service.create_team(db, workspace_id, team_in.hackathon_id, team_in, membership.user)

@router.patch("/workspaces/{workspace_id}/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    team_in: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    team_membership = Depends(require_team_lead_or_colead)
):
    return await team_service.update_team(db, workspace_id, team_id, team_in, membership.user)

@router.get("/workspaces/{workspace_id}/teams/{team_id}/talent-matches")
async def get_talent_matches(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await MatchService.evaluate_talent_matches(db, workspace_id, team_id)

@router.post("/workspaces/{workspace_id}/teams/{team_id}/apply")
async def apply_to_team(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await MatchService.apply_to_team(db, workspace_id, team_id, membership.user)

@router.post("/workspaces/{workspace_id}/teams/{team_id}/invite/{person_id}")
async def invite_to_team(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    team_membership = Depends(require_team_lead_or_colead)
):
    return await MatchService.invite_to_team(db, workspace_id, team_id, person_id, membership.user)
