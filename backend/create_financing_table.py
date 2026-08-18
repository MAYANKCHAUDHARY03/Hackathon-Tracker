import asyncio
from app.database import engine
from app.models.financing import FundingOpportunity

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(FundingOpportunity.__table__.create, checkfirst=True)
        print("Created funding opportunity table")

if __name__ == "__main__":
    asyncio.run(main())
