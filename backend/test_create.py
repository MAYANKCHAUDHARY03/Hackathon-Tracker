import asyncio
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db.sqlite"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)

async def test_create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(test_create())
