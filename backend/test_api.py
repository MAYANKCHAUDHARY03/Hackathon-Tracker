import asyncio
import httpx
import uuid

async def test():
    async with httpx.AsyncClient() as client:
        email = f"test_{uuid.uuid4()}@example.com"
        # Register
        res = await client.post("http://localhost:8000/api/v1/auth/register", json={
            "full_name": "Test User",
            "email": email,
            "password": "password123"
        })
        print("Register:", res.status_code)
        token = res.json()["access_token"]
        
        # Get workspaces
        res = await client.get("http://localhost:8000/api/v1/workspaces", headers={
            "Authorization": f"Bearer {token}"
        })
        print("Workspaces:", res.status_code, res.text)

asyncio.run(test())
