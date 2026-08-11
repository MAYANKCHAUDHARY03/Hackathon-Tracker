import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import get_current_user, require_workspace_admin
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.user import User

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
        return MockUser(id=mock_user_id, email="admin@test.com")
    def _override_access():
        return MockUser(id=mock_user_id, email="admin@test.com")
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_workspace_admin] = _override_access
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_trust_verification_flow(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Trust WS", slug="trust-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # Create Verification Request
    entity_id = str(uuid.uuid4())
    resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/verifications",
        json={
            "entity_type": "user",
            "entity_id": entity_id,
            "achievement_type": "skill",
            "achievement_detail": "Python",
            "source": "AI Assistant"
        }
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["source"] == "AI Assistant"
    
    verification_id = data["id"]
    
    # Verify the achievement
    verify_resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/verifications/{verification_id}/verify"
    )
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["status"] == "verified"
    assert v_data["verifier_id"] == str(mock_user_id)
    assert v_data["verified_at"] is not None

    # Reject the achievement
    reject_resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/verifications/{verification_id}/reject"
    )
    assert reject_resp.status_code == 200
    r_data = reject_resp.json()
    assert r_data["status"] == "rejected"
    assert r_data["verifier_id"] == str(mock_user_id)
