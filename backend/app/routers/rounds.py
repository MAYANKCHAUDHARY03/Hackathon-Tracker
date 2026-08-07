import uuid
from typing import List
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.round import HackathonRoundCreate, HackathonRoundResponse, DeadlineCreate, DeadlineResponse
from app.services.round_service import get_rounds_for_hackathon, create_round, get_deadlines_for_hackathon, create_deadline

router = APIRouter(prefix="/hackathons/{hackathon_id}/rounds", tags=["Rounds"])

@router.get("", response_model=List[HackathonRoundResponse])
async def list_rounds(
    hackathon_id: uuid.UUID,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_rounds_for_hackathon(db, x_workspace_id, hackathon_id)

@router.post("", response_model=HackathonRoundResponse)
async def add_round(
    hackathon_id: uuid.UUID,
    round_in: HackathonRoundCreate,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_round(db, x_workspace_id, hackathon_id, round_in, current_user)

@router.get("/deadlines", response_model=List[DeadlineResponse])
async def read_deadlines(
    hackathon_id: uuid.UUID,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_deadlines_for_hackathon(db, x_workspace_id, hackathon_id)

@router.post("/deadlines", response_model=DeadlineResponse)
async def add_deadline(
    hackathon_id: uuid.UUID,
    deadline_in: DeadlineCreate,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_deadline(db, x_workspace_id, hackathon_id, deadline_in, current_user)
