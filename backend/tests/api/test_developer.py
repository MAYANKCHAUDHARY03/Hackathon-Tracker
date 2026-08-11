import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import verify_workspace_access, require_workspace_admin
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

mock_user_id = uuid.uuid4()
class MockUser:
    def __init__(self, id, email):
        self.id = id
        self.user_id = id
        self.email = email
        self.is_active = True

@pytest.fixture
def override_deps():
    def _override_user():
        return MockUser(id=mock_user_id, email="admin@test.com")
    def _override_access():
        return MockUser(id=mock_user_id, email="admin@test.com")
    app.dependency_overrides[verify_workspace_access] = _override_user
    app.dependency_overrides[require_workspace_admin] = _override_access
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_developer_ecosystem(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Dev WS", slug="dev-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # 1. Create Developer App
    app_res = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/developer/apps",
        json={
            "name": "Integration Test App",
            "redirect_uris": ["https://example.com/callback"]
        }
    )
    assert app_res.status_code == 200
    app_data = app_res.json()
    assert app_data["name"] == "Integration Test App"
    assert "client_id" in app_data
    assert "client_secret" in app_data

    # 2. Create Webhook
    hook_res = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/developer/webhooks",
        json={
            "url": "https://example.com/webhook",
            "events": ["project.created"]
        }
    )
    assert hook_res.status_code == 200
    hook_data = hook_res.json()
    assert hook_data["url"] == "https://example.com/webhook"
    assert "secret" in hook_data
