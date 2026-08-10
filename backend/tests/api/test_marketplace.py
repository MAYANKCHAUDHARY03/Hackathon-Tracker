import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.organization import Organization
from app.models.sponsor import Sponsor
from app.models.graph import GraphEdge
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

@pytest.mark.asyncio
async def test_get_projects_seeking_partners(
    async_client: AsyncClient,
    db_session: AsyncSession,
    override_get_current_user
):
    workspace_id = uuid.uuid4()
    
    # Needs a Workspace to satisfy foreign key
    from app.models.workspace import Workspace
    workspace = Workspace(
        id=workspace_id,
        name="Test Workspace",
        slug=f"test-workspace-{uuid.uuid4()}"
    )
    db_session.add(workspace)
    
    from app.models.user import WorkspaceMembership
    membership = WorkspaceMembership(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        user_id=mock_user_id,
        role="MEMBER"
    )
    db_session.add(membership)
    
    from app.models.hackathon import Hackathon
    hackathon_id = uuid.uuid4()
    from datetime import datetime, timedelta, UTC
    now = datetime.now(UTC)
    hackathon = Hackathon(
        id=hackathon_id,
        workspace_id=workspace_id,
        name="Test Hackathon",
        status="ACTIVE",
        registration_deadline=now + timedelta(days=1),
        start_date=now + timedelta(days=2),
        end_date=now + timedelta(days=3),
    )
    db_session.add(hackathon)
    
    from app.models.team import Team
    
    t1_id = uuid.uuid4()
    t1 = Team(id=t1_id, workspace_id=workspace_id, hackathon_id=hackathon_id, name="Test Team 1", slug=f"test-team-1-{uuid.uuid4()}")
    db_session.add(t1)
    
    # 1. Create a Project seeking partners
    p1_id = uuid.uuid4()
    p1 = Project(
        id=p1_id,
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        team_id=t1_id,
        title="Test Project 1",
        slug=f"test-project-1-{uuid.uuid4()}",
        status="PILOT"
    )
    db_session.add(p1)

    t2_id = uuid.uuid4()
    t2 = Team(id=t2_id, workspace_id=workspace_id, hackathon_id=hackathon_id, name="Test Team 2", slug=f"test-team-2-{uuid.uuid4()}")
    db_session.add(t2)

    # 2. Create another project seeking partners
    p2_id = uuid.uuid4()
    p2 = Project(
        id=p2_id,
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        team_id=t2_id,
        title="Test Project 2",
        slug=f"test-project-2-{uuid.uuid4()}",
        status="INCUBATION"
    )
    db_session.add(p2)

    t3_id = uuid.uuid4()
    t3 = Team(id=t3_id, workspace_id=workspace_id, hackathon_id=hackathon_id, name="Test Team 3", slug=f"test-team-3-{uuid.uuid4()}")
    db_session.add(t3)

    # 3. Create a project NOT seeking partners
    p3_id = uuid.uuid4()
    p3 = Project(
        id=p3_id,
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        team_id=t3_id,
        title="Test Project 3",
        slug=f"test-project-3-{uuid.uuid4()}",
        status="IDEA"
    )
    
    db_session.add(p3)
    await db_session.commit()
    
    response = await async_client.get(f"/api/v1/marketplace/projects?workspace_id={workspace_id}")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    
    projects = data["projects"]
    assert len(projects) == 2
    statuses = [p["status"] for p in projects]
    assert "PILOT" in statuses
    assert "INCUBATION" in statuses
    assert "IDEA" not in statuses

@pytest.mark.asyncio
async def test_get_partners_seeking_projects(
    async_client: AsyncClient,
    db_session: AsyncSession,
    override_get_current_user
):
    workspace_id = uuid.uuid4()
    
    # Needs a Workspace
    from app.models.workspace import Workspace
    workspace = Workspace(
        id=workspace_id,
        name="Test Workspace",
        slug=f"test-workspace-{uuid.uuid4()}"
    )
    db_session.add(workspace)
    
    from app.models.user import WorkspaceMembership
    membership = WorkspaceMembership(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        user_id=mock_user_id,
        role="MEMBER"
    )
    db_session.add(membership)
    
    org1 = Organization(
        id=uuid.uuid4(),
        name="Test Org 1",
        slug=f"test-org-{uuid.uuid4()}",
        ecosystem_opt_in=True
    )
    
    sponsor1 = Sponsor(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name="Test Sponsor 1",
        slug=f"test-sponsor-{uuid.uuid4()}"
    )
    
    db_session.add_all([org1, sponsor1])
    await db_session.commit()
    
    response = await async_client.get(f"/api/v1/marketplace/partners?workspace_id={workspace_id}")
    assert response.status_code == 200
    data = response.json()
    assert "partners" in data
    
    partners = data["partners"]
    assert len(partners) == 2
    types = [p["type"] for p in partners]
    assert "Organization" in types
    assert "Sponsor" in types
