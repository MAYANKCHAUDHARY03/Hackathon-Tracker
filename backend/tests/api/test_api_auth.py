import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import get_current_user, require_workspace_admin, verify_workspace_access
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.user import User
from app.services.api_auth_service import APIKeyService

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

mock_user_id = uuid.uuid4()
class MockUser:
    def __init__(self, id, email):
        self.id = id
        self.email = email
        self.is_active = True

@pytest.fixture
def override_deps():
    def _override_user():
        return MockUser(id=mock_user_id, email="test@test.com")
        
    def _override_access():
        return True
        
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_workspace_admin] = _override_access
    app.dependency_overrides[verify_workspace_access] = _override_access
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_and_list_api_keys(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Test Workspace", slug="test-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    headers = {"Authorization": "Bearer fake_token"}
    payload = {
        "name": "Test Key",
        "scopes": ["hackathons:read", "hackathons:write"]
    }
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/api-keys",
        headers=headers,
        json=payload
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Key"
    assert "key" in data  # Raw key is returned once
    assert data["prefix"] == "ht_live_"
    
    # List keys
    list_resp = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/api-keys",
        headers=headers
    )
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert len(list_data) == 1
    assert "key" not in list_data[0] # Raw key is never returned again
    
    key_id = data["id"]
    
    # Revoke key
    revoke_resp = await async_client.delete(
        f"/api/v1/workspaces/{workspace.id}/api-keys/{key_id}",
        headers=headers
    )
    assert revoke_resp.status_code == 204
    
    # Check it is inactive
    list_resp2 = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/api-keys",
        headers=headers
    )
    assert list_resp2.status_code == 200
    assert list_resp2.json()[0]["is_active"] is False
