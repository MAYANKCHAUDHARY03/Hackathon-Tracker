import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, verify_workspace_access
from app.models.user import User, WorkspaceMembership
from app.schemas.outcome import HackathonResultCreate, HackathonResultUpdate, HackathonResultResponse, RewardCreate, RewardUpdate, RewardResponse, AchievementCreate, AchievementUpdate, AchievementResponse
from app.services import outcome_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}/hackathons/{hackathon_id}",
    tags=["outcomes"]
)

@router.get("/results", response_model=List[HackathonResultResponse])
async def list_results(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await outcome_service.get_results(db, workspace_id, hackathon_id)

@router.post("/results", response_model=HackathonResultResponse)
async def create_result(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    result_in: HackathonResultCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    result_in.hackathon_id = hackathon_id
    return await outcome_service.create_result(db, workspace_id, current_user.id, result_in)

@router.get("/rewards", response_model=List[RewardResponse])
async def list_rewards(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await outcome_service.get_rewards(db, workspace_id, hackathon_id)

@router.post("/rewards", response_model=RewardResponse)
async def create_reward(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    reward_in: RewardCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    reward_in.hackathon_id = hackathon_id
    return await outcome_service.create_reward(db, workspace_id, current_user.id, reward_in)

@router.get("/achievements", response_model=List[AchievementResponse])
async def list_achievements(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await outcome_service.get_achievements(db, workspace_id, hackathon_id)

@router.post("/achievements", response_model=AchievementResponse)
async def create_achievement(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    achievement_in: AchievementCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    achievement_in.hackathon_id = hackathon_id
    return await outcome_service.create_achievement(db, workspace_id, current_user.id, achievement_in)
