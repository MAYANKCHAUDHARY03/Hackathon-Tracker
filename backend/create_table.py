import asyncio
from app.database import engine
from app.models.base import Base
from app.models.forecast import Forecast

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Created all missing tables")

if __name__ == "__main__":
    asyncio.run(main())
