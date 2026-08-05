import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.round import HackathonRound, Deadline, RoundProgress
from app.models.hackathon import Hackathon
from app.schemas.round import HackathonRoundCreate, HackathonRoundUpdate, DeadlineCreate, DeadlineUpdate
from app.models.user import User

async def get_rounds_for_hackathon(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[HackathonRound]:
    stmt = select(HackathonRound).where(
        HackathonRound.workspace_id == workspace_id,
        HackathonRound.hackathon_id == hackathon_id
    ).order_by(HackathonRound.sequence)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_round(
    db: AsyncSession, 
    workspace_id: uuid.UUID, 
    hackathon_id: uuid.UUID, 
    round_in: HackathonRoundCreate,
    current_user: User
) -> HackathonRound:
    
    # Check if hackathon exists and belongs to workspace
    stmt = select(Hackathon).where(Hackathon.id == hackathon_id, Hackathon.workspace_id == workspace_id)
    result = await db.execute(stmt)
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Hackathon not found")

    # Ensure sequence is unique for this hackathon
    stmt_seq = select(HackathonRound).where(
        HackathonRound.hackathon_id == hackathon_id,
        HackathonRound.sequence == round_in.sequence
    )
    result_seq = await db.execute(stmt_seq)
    if result_seq.scalars().first():
        raise HTTPException(status_code=400, detail="Round with this sequence already exists")

    new_round = HackathonRound(
        **round_in.model_dump(),
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        created_by=current_user.id
    )
    db.add(new_round)
    await db.commit()
    await db.refresh(new_round)
    return new_round

async def get_deadlines_for_hackathon(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[Deadline]:
    stmt = select(Deadline).where(
        Deadline.workspace_id == workspace_id,
        Deadline.hackathon_id == hackathon_id
    ).order_by(Deadline.due_at)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_deadline(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    deadline_in: DeadlineCreate,
    current_user: User
) -> Deadline:
    new_deadline = Deadline(
        **deadline_in.model_dump(),
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        created_by=current_user.id
    )
    db.add(new_deadline)
    await db.commit()
    await db.refresh(new_deadline)
    return new_deadline
