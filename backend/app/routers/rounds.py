import uuid
from typing import List
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, verify_workspace_access_header
from app.models.user import User, WorkspaceMembership
from app.schemas.round import HackathonRoundCreate, HackathonRoundResponse, DeadlineCreate, DeadlineResponse
from app.services.round_service import get_rounds_for_hackathon, create_round, get_deadlines_for_hackathon, create_deadline

router = APIRouter(prefix="/hackathons/{hackathon_id}/rounds", tags=["Rounds"])

@router.get("", response_model=List[HackathonRoundResponse])
async def list_rounds(
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access_header)
):
    return await get_rounds_for_hackathon(db, membership.workspace_id, hackathon_id)

@router.post("", response_model=HackathonRoundResponse)
async def add_round(
    hackathon_id: uuid.UUID,
    round_in: HackathonRoundCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access_header)
):
    return await create_round(db, membership.workspace_id, hackathon_id, round_in, membership.user)

@router.get("/deadlines", response_model=List[DeadlineResponse])
async def read_deadlines(
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access_header)
):
    return await get_deadlines_for_hackathon(db, membership.workspace_id, hackathon_id)

@router.post("/deadlines", response_model=DeadlineResponse)
async def add_deadline(
    hackathon_id: uuid.UUID,
    deadline_in: DeadlineCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access_header)
):
    return await create_deadline(db, membership.workspace_id, hackathon_id, deadline_in, membership.user)
