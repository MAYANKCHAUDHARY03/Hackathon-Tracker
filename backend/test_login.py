import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth_service import verify_password
from sqlalchemy import select

async def main():
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.email == "bob@gmail.com")
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print("User not found")
            else:
                print("User found", user.id)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
