import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User, WorkspaceMembership
from app.models.workspace import Workspace
from app.services.auth_service import get_password_hash
import re

def generate_slug(name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-').lower()
    return slug

async def main():
    try:
        async with AsyncSessionLocal() as db:
            new_user = User(
                full_name="Test User",
                email="test5@example.com",
                password_hash=get_password_hash("password123")
            )
            db.add(new_user)
            await db.flush() # flush to get user ID
            
            base_slug = generate_slug(f"Test User workspace")
            slug = f"{base_slug}-{str(new_user.id)[:8]}"
            
            new_workspace = Workspace(
                name=f"Test User's Workspace",
                slug=slug
            )
            db.add(new_workspace)
            await db.flush() # flush to get workspace ID
            
            membership = WorkspaceMembership(
                user_id=new_user.id,
                workspace_id=new_workspace.id,
                role="owner"
            )
            db.add(membership)
            
            await db.commit()
            print("Successfully registered")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
