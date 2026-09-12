import pytest
import uuid
from httpx import AsyncClient
from app.models.memory import MemoryType

@pytest.mark.asyncio
async def test_create_and_get_memory(async_client: AsyncClient):
    # Register and get token
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": f"memory_{uuid.uuid4()}@example.com", "full_name": "Memory User", "password": "password123"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get workspaces
    workspaces_response = await async_client.get("/api/v1/workspaces", headers=headers)
    test_workspace_id = workspaces_response.json()[0]["id"]

    # Create
    response = await async_client.post(
        f"/api/v1/memories?workspace_id={test_workspace_id}",
        headers=headers,
        json={
            "agent_name": "test_agent",
            "memory_type": MemoryType.TASK.value,
            "content": {"key": "value"}
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["agent_name"] == "test_agent"
    memory_id = data["id"]
    
    # Get
    response = await async_client.get(
        f"/api/v1/memories/test_agent?workspace_id={test_workspace_id}",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) > 0
    assert any(m["id"] == memory_id for m in data)
    
    # Delete
    response = await async_client.delete(
        f"/api/v1/memories/{memory_id}?workspace_id={test_workspace_id}",
        headers=headers
    )
    assert response.status_code == 200, response.text

@pytest.mark.asyncio
async def test_memory_isolation(async_client: AsyncClient):
    # Register and get token
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": f"memory_iso_{uuid.uuid4()}@example.com", "full_name": "Memory Iso User", "password": "password123"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    other_workspace_id = str(uuid.uuid4())
    # Fails if we don't have access to this workspace or workspace doesn't exist
    response = await async_client.post(
        f"/api/v1/memories?workspace_id={other_workspace_id}",
        headers=headers,
        json={
            "agent_name": "test_agent",
            "memory_type": MemoryType.TASK.value,
            "content": {"key": "value"}
        }
    )
    assert response.status_code in (403, 404, 422), response.text
