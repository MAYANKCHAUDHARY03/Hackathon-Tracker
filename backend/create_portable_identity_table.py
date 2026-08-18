import asyncio
from app.database import engine
from app.models.portable_identity import PortableIdentity, VerifiedSkill
from app.models.base import Base

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(PortableIdentity.__table__.create, checkfirst=True)
        await conn.run_sync(VerifiedSkill.__table__.create, checkfirst=True)
        print("Created tables successfully")

if __name__ == "__main__":
    asyncio.run(main())
