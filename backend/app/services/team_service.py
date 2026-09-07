import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.team import Team
from app.models.workspace import Workspace
from app.schemas.team import TeamCreate, TeamUpdate
from app.models.user import User

async def get_teams(db: AsyncSession, workspace_id: uuid.UUID):
    stmt = select(Team).where(Team.workspace_id == workspace_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_team(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID | None, team_in: TeamCreate, user: User):
    import re
    from app.models.hackathon import Hackathon
    
    if not hackathon_id:
        stmt = select(Hackathon).where(Hackathon.workspace_id == workspace_id).order_by(Hackathon.created_at.desc())
        result = await db.execute(stmt)
        hackathon = result.scalars().first()
        if not hackathon:
            raise HTTPException(status_code=400, detail="No active hackathon found in this workspace")
        hackathon_id = hackathon.id

    slug = re.sub(r'[^a-z0-9]+', '-', team_in.name.lower()).strip('-')
    team = Team(
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        name=team_in.name,
        slug=slug,
        description=team_in.description,
        skills_needed=team_in.skills_needed,
        status='active',
        created_by=user.id
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team

async def get_team(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID):
    stmt = select(Team).where(Team.workspace_id == workspace_id, Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

async def update_team(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID, team_in: TeamUpdate, user: User):
    team = await get_team(db, workspace_id, team_id)
    
    update_data = team_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
        
    await db.commit()
    await db.refresh(team)
    return team
