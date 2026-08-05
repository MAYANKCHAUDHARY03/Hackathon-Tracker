import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_registration(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "full_name": "Test User", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_user_login(async_client: AsyncClient):
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "full_name": "Login User", "password": "password123"}
    )
    
    # Then login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_get_current_user_and_workspaces(async_client: AsyncClient):
    # Register and get token
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "full_name": "Me User", "password": "password123"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current user
    me_response = await async_client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "me@example.com"
    assert me_data["full_name"] == "Me User"
    
    # Get workspaces
    workspaces_response = await async_client.get("/api/v1/workspaces", headers=headers)
    assert workspaces_response.status_code == 200
    workspaces = workspaces_response.json()
    assert len(workspaces) == 1
    assert workspaces[0]["name"] == "Me User's Workspace"
