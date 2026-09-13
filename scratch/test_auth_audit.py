import asyncio
import httpx
from pydantic import BaseModel

API_URL = "http://localhost:8000/api/v1"

async def test_auth():
    async with httpx.AsyncClient(base_url=API_URL) as client:
        # 1. No token
        res = await client.get("/users/me")
        print(f"No token: {res.status_code}")
        assert res.status_code == 401

        # 2. Invalid token
        res = await client.get("/users/me", headers={"Authorization": "Bearer invalid_token_abc"})
        print(f"Invalid token: {res.status_code}")
        assert res.status_code == 401

        print("[PASS] Authentication boundary tests")

if __name__ == "__main__":
    asyncio.run(test_auth())
