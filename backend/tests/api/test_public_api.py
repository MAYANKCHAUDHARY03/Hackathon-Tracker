import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import get_current_user, require_workspace_admin, verify_workspace_access
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from datetime import datetime, timedelta

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
async def test_public_api_hackathons(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Test Workspace", slug="test-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    hackathon = Hackathon(
        workspace_id=workspace.id,
        name="Test Hackathon",
        description="Test",
        start_date=datetime.utcnow() + timedelta(days=5),
        end_date=datetime.utcnow() + timedelta(days=12),
        registration_deadline=datetime.utcnow() + timedelta(days=2),
        status="draft"
    )
    db_session.add(hackathon)
    await db_session.commit()
    await db_session.refresh(hackathon)
    
    # First, generate an API key
    headers = {"Authorization": "Bearer fake_token"}
    payload = {
        "name": "Public API Key",
        "scopes": ["hackathons:read"]
    }
    
    resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/api-keys",
        headers=headers,
        json=payload
    )
    assert resp.status_code == 201
    raw_key = resp.json()["key"]
    
    # Now, test the public API with this key
    public_headers = {"X-API-Key": raw_key}
    
    public_resp = await async_client.get(
        "/api/v1/hackathons",
        headers=public_headers
    )
    assert public_resp.status_code == 200
    data = public_resp.json()
    assert len(data) >= 1
    
    # Test without API key
    fail_resp = await async_client.get("/api/v1/hackathons")
    assert fail_resp.status_code == 401
    
    # Test with invalid API key
    fail_resp2 = await async_client.get(
        "/api/v1/hackathons",
        headers={"X-API-Key": "ht_live_invalidkey123"}
    )
    assert fail_resp2.status_code == 401
    
    # Test with insufficient scopes
    resp2 = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/api-keys",
        headers=headers,
        json={"name": "No Scopes Key", "scopes": []}
    )
    assert resp2.status_code == 201
    raw_key2 = resp2.json()["key"]
    
    fail_resp3 = await async_client.get(
        "/api/v1/hackathons",
        headers={"X-API-Key": raw_key2}
    )
    assert fail_resp3.status_code == 403
