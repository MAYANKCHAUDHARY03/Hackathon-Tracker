import pytest
import uuid
from httpx import AsyncClient
from app.models.memory import MemoryType

@pytest.mark.asyncio
async def test_create_and_get_memory(async_client: AsyncClient, test_user_token: str, test_workspace_id: uuid.UUID):
    # Create
    response = await async_client.post(
        f"/api/v1/memories?workspace_id={test_workspace_id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "agent_name": "test_agent",
            "memory_type": MemoryType.TASK,
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
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) > 0
    assert any(m["id"] == memory_id for m in data)
    
    # Delete
    response = await async_client.delete(
        f"/api/v1/memories/{memory_id}?workspace_id={test_workspace_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200, response.text

@pytest.mark.asyncio
async def test_memory_isolation(async_client: AsyncClient, test_user_token: str, test_workspace_id: uuid.UUID):
    other_workspace_id = str(uuid.uuid4())
    # Fails if we don't have access to this workspace or workspace doesn't exist
    response = await async_client.post(
        f"/api/v1/memories?workspace_id={other_workspace_id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "agent_name": "test_agent",
            "memory_type": MemoryType.TASK,
            "content": {"key": "value"}
        }
    )
    assert response.status_code in (403, 404, 422), response.text
