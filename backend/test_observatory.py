import asyncio
import uuid
from app.database import AsyncSessionLocal
from app.services.observatory_service import ObservatoryService

async def main():
    async with AsyncSessionLocal() as db:
        # Just use a dummy UUID
        dummy_id = uuid.uuid4()
        try:
            stats = await ObservatoryService.get_workspace_stats(dummy_id, db)
            print("SUCCESS:")
            print(stats)
        except Exception as e:
            print("ERROR:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
