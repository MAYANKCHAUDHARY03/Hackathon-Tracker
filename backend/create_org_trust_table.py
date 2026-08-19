import asyncio
from app.database import engine
from app.models.organization_trust import OrganizationTrust

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(OrganizationTrust.__table__.create, checkfirst=True)
        print("Created organization trusts table")

if __name__ == "__main__":
    asyncio.run(main())
