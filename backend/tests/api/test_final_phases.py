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
async def test_governance_and_network(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Global WS", slug="global-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # 1. Governance DSR
    dsr_res = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/governance/dsr",
        json={
            "request_type": "export",
            "details": "Export all my participation data"
        }
    )
    assert dsr_res.status_code == 200
    dsr_data = dsr_res.json()
    assert dsr_data["status"] == "pending"

    # 2. Network Resolve
    net_res = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/network/resolve",
        json={
            "query": "Ocean projects",
            "include_impact_metrics": False
        }
    )
    assert net_res.status_code == 200
    net_data = net_res.json()
    assert len(net_data["nodes"]) == 3
    assert len(net_data["edges"]) == 2
    assert net_data["nodes"][0]["name"] == "Save the Oceans"
