import asyncio
import uuid
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import settings
from app.models.base import BaseEntity
from app.models.hackathon import Hackathon
from app.models.team import Team
from app.models.project import Project

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def run_load_test():
    async with AsyncSessionLocal() as session:
        # Create a workspace
        workspace_id = str(uuid.uuid4())
        
        # Insert 500 hackathons
        hackathons = []
        for i in range(50): # 50 hackathons
            h = Hackathon(
                id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                name=f"Load Test Hackathon {i}",
                description="Load test description",
                status="draft"
            )
            hackathons.append(h)
            session.add(h)
            
        await session.commit()
        
        # Insert 500 teams
        for i in range(500):
            t = Team(
                id=str(uuid.uuid4()),
                hackathon_id=hackathons[0].id,
                name=f"Load Test Team {i}"
            )
            session.add(t)
            
        await session.commit()
        print("Inserted 50 hackathons and 500 teams for testing.")

if __name__ == "__main__":
    asyncio.run(run_load_test())
