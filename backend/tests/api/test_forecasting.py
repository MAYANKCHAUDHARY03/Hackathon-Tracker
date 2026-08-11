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
async def test_forecasting_project(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Forecast WS", slug="forecast-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    h = Hackathon(
        workspace_id=workspace.id, 
        name="Test Hackathon", 
        registration_deadline=datetime.now(UTC),
        start_date=datetime.now(UTC), 
        end_date=datetime.now(UTC)
    )
    db_session.add(h)
    await db_session.commit()
    await db_session.refresh(h)
    
    t = Team(workspace_id=workspace.id, hackathon_id=h.id, name="Test Team", slug="test-team-3")
    db_session.add(t)
    await db_session.commit()
    await db_session.refresh(t)

    # Setup test project for context
    project = Project(
        workspace_id=workspace.id,
        hackathon_id=h.id,
        team_id=t.id,
        title="Predictive AI Tool",
        slug="predictive-ai-tool",
        description="A tool that predicts.",
        created_by=uuid.uuid4()
    )
    db_session.add(project)
    await db_session.commit()
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/forecasting/projects/{project.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["is_prediction"] is True
    assert "confidence" in data
    assert "factors" in data
