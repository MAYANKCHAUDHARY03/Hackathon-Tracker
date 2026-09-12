import asyncio
import sys
import uuid
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.workspace import Workspace
from app.models.user import WorkspaceMembership

async def test():
    async with AsyncSessionLocal() as db:
        current_user_id = uuid.UUID('92b406addedc469591b423920ea3ffb9')
        stmt = (
            select(Workspace)
            .join(WorkspaceMembership)
            .where(WorkspaceMembership.user_id == current_user_id)
        )
        res = await db.execute(stmt)
        print(res.scalars().all())

if __name__ == "__main__":
    asyncio.run(test())
