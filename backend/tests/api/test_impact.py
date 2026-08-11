import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import verify_workspace_access, require_workspace_admin
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.hackathon import Hackathon
from app.models.team import Team
from datetime import datetime, UTC

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
async def test_impact_measurement(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Impact WS", slug="impact-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # 1. Create custom metric
    res = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/impact/metrics",
        json={"name": "GHG Reduced", "unit": "Tons CO2"}
    )
    assert res.status_code == 200
    assert res.json()["name"] == "GHG Reduced"
    
    # Setup test project
    h = Hackathon(workspace_id=workspace.id, name="TH", registration_deadline=datetime.now(UTC), start_date=datetime.now(UTC), end_date=datetime.now(UTC))
    db_session.add(h)
    await db_session.commit()
    t = Team(workspace_id=workspace.id, hackathon_id=h.id, name="TT", slug="tt-impact")
    db_session.add(t)
    await db_session.commit()
    p = Project(workspace_id=workspace.id, hackathon_id=h.id, team_id=t.id, title="P1", slug="p1-impact", created_by=uuid.uuid4())
    db_session.add(p)
    await db_session.commit()
    
    # 2. Update project funnel and metrics
    res2 = await async_client.put(
        f"/api/v1/workspaces/{workspace.id}/impact/projects/{p.id}",
        json={
            "stage": "Pilot",
            "jobs_created": 5,
            "custom_metrics": {"GHG Reduced": 100}
        }
    )
    assert res2.status_code == 200
    data = res2.json()
    assert data["stage"] == "Pilot"
    assert data["jobs_created"] == 5
    assert data["custom_metrics"]["GHG Reduced"] == 100
