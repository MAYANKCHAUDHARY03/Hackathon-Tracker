import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from datetime import datetime, UTC
import uuid

from app.models.project import Project, Technology, ProjectTechnology
from app.models.workspace import Workspace
from app.main import app
from app.dependencies import get_current_user
from tests.conftest import TestingSessionLocal

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

class MockUser:
    def __init__(self, id, role, email):
        self.id = id
        self.role = role
        self.email = email

mock_user_id = uuid.uuid4()

@pytest.fixture
def override_get_current_user():
    def _override():
        return MockUser(id=mock_user_id, role="USER", email="test@test.com")
    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.pop(get_current_user)

@pytest.fixture
async def sample_intelligence_data(db_session: AsyncSession):
    # Setup test workspace
    workspace_id = uuid.uuid4()
    workspace = Workspace(id=workspace_id, name="Test Workspace", slug=f"test-workspace-{uuid.uuid4()}")
    db_session.add(workspace)

    # Note: For intelligence to work, we need some hackathons and projects, 
    # but the queries in intelligence_service aggregate over all projects.
    # We will just add some basic technologies and projects.
    
    t1_id = uuid.uuid4()
    t1 = Technology(id=t1_id, name="React", slug="react", category="Frontend")
    db_session.add(t1)
    
    t2_id = uuid.uuid4()
    t2 = Technology(id=t2_id, name="Python", slug="python", category="Backend")
    db_session.add(t2)

    await db_session.commit()
    
    from app.models.hackathon import Hackathon
    hackathon_id = uuid.uuid4()
    hackathon = Hackathon(
        id=hackathon_id,
        workspace_id=workspace_id,
        name="Test Hackathon",
        status="ACTIVE",
        registration_deadline=datetime.now(UTC),
        start_date=datetime.now(UTC),
        end_date=datetime.now(UTC)
    )
    db_session.add(hackathon)
    await db_session.commit()
    
    from app.models.team import Team
    team_id = uuid.uuid4()
    team = Team(id=team_id, workspace_id=workspace_id, hackathon_id=hackathon_id, name="Test Team", slug=f"test-team-{uuid.uuid4()}")
    db_session.add(team)
    await db_session.commit()

    # Create projects
    p1_id = uuid.uuid4()
    p1 = Project(
        id=p1_id,
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        team_id=team_id,
        title="Project 1",
        slug=f"proj-1-{uuid.uuid4()}",
        status="completed",
        created_at=datetime.now(UTC)
    )
    db_session.add(p1)
    
    await db_session.commit()

    pt1 = ProjectTechnology(project_id=p1_id, technology_id=t1_id)
    pt2 = ProjectTechnology(project_id=p1_id, technology_id=t2_id)
    db_session.add(pt1)
    db_session.add(pt2)
    
    await db_session.commit()
    return p1

@pytest.mark.asyncio
async def test_get_ecosystem_analytics(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_intelligence_data,
    override_get_current_user
):
    response = await async_client.get("/api/v1/intelligence/ecosystem")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "total_projects" in data
    assert data["total_projects"] >= 1
    
    assert "total_technologies" in data
    assert data["total_technologies"] >= 2
    
    assert "top_technologies" in data
    techs = [t["technology_name"] for t in data["top_technologies"]]
    assert "React" in techs
    assert "Python" in techs
    
    assert "project_status_distribution" in data
    statuses = [s["status"] for s in data["project_status_distribution"]]
    assert "completed" in statuses
    
    assert "participation_trends" in data
