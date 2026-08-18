import asyncio
from app.database import engine
from app.models.trust_verification import TrustVerification

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(TrustVerification.__table__.create, checkfirst=True)
        print("Created trust verification table")

if __name__ == "__main__":
    asyncio.run(main())
