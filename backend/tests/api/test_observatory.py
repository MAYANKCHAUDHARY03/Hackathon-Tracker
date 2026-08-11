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
from app.models.impact import ProjectImpact
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
async def test_observatory_stats(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Obs WS", slug="obs-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    h1 = Hackathon(workspace_id=workspace.id, name="H1", registration_deadline=datetime.now(UTC), start_date=datetime.now(UTC), end_date=datetime.now(UTC))
    h2 = Hackathon(workspace_id=workspace.id, name="H2", registration_deadline=datetime.now(UTC), start_date=datetime.now(UTC), end_date=datetime.now(UTC))
    db_session.add_all([h1, h2])
    await db_session.commit()
    
    # We also need a team for projects
    from app.models.team import Team
    t1 = Team(workspace_id=workspace.id, hackathon_id=h1.id, name="T1", slug="t1-obs")
    t2 = Team(workspace_id=workspace.id, hackathon_id=h2.id, name="T2", slug="t2-obs")
    db_session.add_all([t1, t2])
    await db_session.commit()
    
    p1 = Project(workspace_id=workspace.id, hackathon_id=h1.id, team_id=t1.id, title="P1", slug="p1-obs", created_by=uuid.uuid4())
    p2 = Project(workspace_id=workspace.id, hackathon_id=h2.id, team_id=t2.id, title="P2", slug="p2-obs", created_by=uuid.uuid4())
    db_session.add_all([p1, p2])
    await db_session.commit()

    impact = ProjectImpact(
        workspace_id=workspace.id,
        project_id=p1.id,
        jobs_created=10,
        funding_raised=50000.0,
        revenue_generated=10000.0
    )
    db_session.add(impact)
    await db_session.commit()
    
    res = await async_client.get(f"/api/v1/workspaces/{workspace.id}/observatory/stats")
    
    assert res.status_code == 200
    data = res.json()
    assert data["total_projects"] == 2
    assert data["total_hackathons"] == 2
    assert data["total_jobs_created"] == 10
    assert data["total_funding_raised"] == 50000.0
    assert data["total_revenue_generated"] == 10000.0
