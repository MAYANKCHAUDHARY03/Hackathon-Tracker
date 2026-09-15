import pytest
from httpx import AsyncClient
import uuid
from app.models.user import User, WorkspaceMembership
from app.models.workspace import Workspace
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def setup_data(db_session: AsyncSession):
    user = User(id=uuid.uuid4(), email="test@test.com", full_name="Test", password_hash="pw", is_active=True)
    workspace = Workspace(id=uuid.uuid4(), name="Test WS", slug="test-ws")
    db_session.add_all([user, workspace])
    await db_session.flush()
    
    membership = WorkspaceMembership(workspace_id=workspace.id, user_id=user.id, role="admin")
    db_session.add(membership)
    await db_session.commit()
    
    from app.config import settings
    from jose import jwt
    token = jwt.encode({"sub": str(user.id)}, settings.SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    return {"user": user, "workspace": workspace, "headers": headers}

async def test_developer_apps_endpoint(async_client: AsyncClient, setup_data):
    workspace = setup_data["workspace"]
    headers = setup_data["headers"]
    
    response = await async_client.get(f"/api/v1/workspaces/{workspace.id}/developer/apps", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

async def test_verifications_endpoint(async_client: AsyncClient, setup_data):
    workspace = setup_data["workspace"]
    headers = setup_data["headers"]
    
    response = await async_client.get(f"/api/v1/workspaces/{workspace.id}/verifications", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_governance_audit_endpoint(async_client: AsyncClient, setup_data):
    workspace = setup_data["workspace"]
    headers = setup_data["headers"]
    
    response = await async_client.get(f"/api/v1/workspaces/{workspace.id}/governance/audit", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_governance_dsr_endpoint(async_client: AsyncClient, setup_data):
    workspace = setup_data["workspace"]
    headers = setup_data["headers"]
    
    response = await async_client.get(f"/api/v1/workspaces/{workspace.id}/governance/dsr", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_financing_matches_endpoint(async_client: AsyncClient, setup_data):
    headers = setup_data["headers"]
    
    response = await async_client.get(f"/api/v1/financing/matches/me", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_notification_preferences_endpoint(async_client: AsyncClient, setup_data):
    workspace = setup_data["workspace"]
    headers = setup_data["headers"]
    
    response = await async_client.get(f"/api/v1/workspaces/{workspace.id}/notification-preferences", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_notification_preferences_put_persistence(async_client: AsyncClient, setup_data):
    workspace = setup_data["workspace"]
    headers = setup_data["headers"]
    
    # 1. GET initial
    resp1 = await async_client.get(f"/api/v1/workspaces/{workspace.id}/notification-preferences", headers=headers)
    assert resp1.status_code == 200
    prefs = resp1.json()
    assert len(prefs) > 0
    target_category = prefs[0]["category"]
    old_value = prefs[0]["in_app_enabled"]
    
    # 2. PUT update
    new_value = not old_value
    resp2 = await async_client.put(
        f"/api/v1/workspaces/{workspace.id}/notification-preferences/{target_category}",
        json={"in_app_enabled": new_value},
        headers=headers
    )
    assert resp2.status_code == 200
    
    # 3. GET again and verify persistence
    resp3 = await async_client.get(f"/api/v1/workspaces/{workspace.id}/notification-preferences", headers=headers)
    updated_prefs = resp3.json()
    updated_category_pref = next(p for p in updated_prefs if p["category"] == target_category)
    assert updated_category_pref["in_app_enabled"] == new_value
