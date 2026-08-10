import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_get_portfolio_requires_auth(async_client: AsyncClient):
    workspace_id = uuid.uuid4()
    response = await async_client.get(f"/api/v1/workspaces/{workspace_id}/portfolio")
    assert response.status_code == 401
