import asyncio
from app.database import AsyncSessionLocal
from app.services.graph_service import GraphQueryService
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text('SELECT id FROM workspaces LIMIT 1'))
        wid = res.scalar()
        if wid:
            service = GraphQueryService(session)
            try:
                print(await service.get_workspace_portfolio(wid))
            except Exception as e:
                print("Error:", e)
        else:
            print('No workspace')

if __name__ == "__main__":
    asyncio.run(main())
