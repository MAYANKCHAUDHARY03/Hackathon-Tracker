import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.models.user import User
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from app.services.team_service import create_team
from app.services.project_service import create_project
from app.schemas.team import TeamCreate
from app.schemas.project import ProjectCreate
import uuid

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with AsyncSessionLocal() as db:
        # Get first user and their workspace
        result = await db.execute(select(User))
        user = result.scalars().first()
        if not user:
            print("No users found")
            return
            
        result = await db.execute(select(Workspace))
        workspace = result.scalars().first()
        if not workspace:
            print("No workspaces found")
            return

        print(f"Seeding for user {user.email} in workspace {workspace.name}")

        from datetime import datetime, timedelta
        now = datetime.utcnow()
        hackathon = Hackathon(workspace_id=workspace.id, name="Test Hackathon", registration_deadline=now, start_date=now, end_date=now + timedelta(days=2))
        db.add(hackathon)
        await db.flush()
        
        team_create = TeamCreate(name="Test Team", hackathon_id=hackathon.id)
        team = await create_team(db, workspace.id, hackathon.id, team_create, user)
        
        project_create = ProjectCreate(name="Phase 4 Kanban Test", description="Testing kanban", hackathon_id=hackathon.id, technologies=[])
        project = await create_project(db, workspace.id, team.id, project_create, user)
        
        await db.commit()
        print("Successfully seeded project and kanban board!")

if __name__ == "__main__":
    asyncio.run(seed())
