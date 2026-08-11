import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import verify_workspace_access, require_workspace_admin
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.federation import FederationStatus

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
async def test_federation_flow(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    source_ws = Workspace(name="Source WS", slug="src-ws", organization_id=uuid.uuid4())
    target_ws = Workspace(name="Target WS", slug="tgt-ws", organization_id=uuid.uuid4())
    db_session.add_all([source_ws, target_ws])
    await db_session.commit()
    await db_session.refresh(source_ws)
    await db_session.refresh(target_ws)
    
    # Create Federation
    create_res = await async_client.post(
        f"/api/v1/workspaces/{source_ws.id}/federation",
        json={"target_workspace_id": str(target_ws.id), "shared_entities": ["projects", "mentors"]}
    )
    assert create_res.status_code == 200
    fed_id = create_res.json()["id"]
    assert create_res.json()["status"] == "pending"

    # List Federation
    list_res = await async_client.get(
        f"/api/v1/workspaces/{source_ws.id}/federation"
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Accept Federation (Simulating Target Workspace)
    update_res = await async_client.put(
        f"/api/v1/workspaces/{target_ws.id}/federation/{fed_id}",
        json={"status": "accepted"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "accepted"
