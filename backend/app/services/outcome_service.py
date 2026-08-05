import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.outcome import HackathonResult, Reward, Achievement
from app.schemas.outcome import HackathonResultCreate, HackathonResultUpdate, RewardCreate, RewardUpdate, AchievementCreate, AchievementUpdate
from datetime import datetime, timezone

async def get_results(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[HackathonResult]:
    query = select(HackathonResult).where(
        HackathonResult.workspace_id == workspace_id,
        HackathonResult.hackathon_id == hackathon_id,
        HackathonResult.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def create_result(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: HackathonResultCreate) -> HackathonResult:
    res = HackathonResult(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(res)
    await db.commit()
    await db.refresh(res)
    return res

async def get_rewards(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[Reward]:
    query = select(Reward).where(
        Reward.workspace_id == workspace_id,
        Reward.hackathon_id == hackathon_id,
        Reward.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def create_reward(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: RewardCreate) -> Reward:
    reward = Reward(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(reward)
    await db.commit()
    await db.refresh(reward)
    return reward

async def get_achievements(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[Achievement]:
    query = select(Achievement).where(
        Achievement.workspace_id == workspace_id,
        Achievement.hackathon_id == hackathon_id,
        Achievement.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def create_achievement(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: AchievementCreate) -> Achievement:
    achievement = Achievement(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        achieved_at=datetime.now(timezone.utc),
        **data.model_dump()
    )
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    return achievement
