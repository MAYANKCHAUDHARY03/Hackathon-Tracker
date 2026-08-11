import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
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
async def test_research_link_lifecycle(
    async_client: AsyncClient,
    db_session: AsyncSession,
    override_get_current_user
):
    workspace_id = uuid.uuid4()
    
    # 1. Setup Models
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
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    hackathon = Hackathon(
        id=hackathon_id,
        workspace_id=workspace_id,
        name="Test Hackathon",
        status="DRAFT",
        registration_deadline=now,
        start_date=now,
        end_date=now
    )
    db_session.add(hackathon)

    from app.models.team import Team
    team_id = uuid.uuid4()
    team = Team(
        id=team_id,
        hackathon_id=hackathon_id,
        workspace_id=workspace_id,
        name="Test Team",
        slug=f"test-team-{uuid.uuid4()}",
        status="ACTIVE"
    )
    db_session.add(team)

    from app.models.project import Project
    project_id = uuid.uuid4()
    project = Project(
        id=project_id,
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        team_id=team_id,
        title="Test Project",
        slug=f"test-project-{uuid.uuid4()}",
        description="Test Description",
        status="idea"
    )
    db_session.add(project)
    
    await db_session.commit()

    # 1. Create a research link
    create_data = {
        "project_id": str(project_id),
        "type": "paper",
        "title": "Quantum Error Correction in Hackathons",
        "url": "https://arxiv.org/abs/fake",
        "identifier": "arxiv:1234.5678",
        "authors": ["Alice Smith", "Bob Jones"],
        "publication_date": "2026-05-01T00:00:00Z"
    }

    # Verify workspace access bypass because test environment
    # Wait, the workspace_auth middleware / verify_workspace_access needs current_user which we mocked,
    # and membership which we added to DB.
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/research/",
        json=create_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Quantum Error Correction in Hackathons"
    assert data["type"] == "paper"
    assert data["provenance"] == "user-provided"
    link_id = data["id"]

    # 2. Get links for project
    response = await async_client.get(
        f"/api/v1/workspaces/{workspace_id}/research/project/{project_id}"
    )
    assert response.status_code == 200
    links = response.json()
    assert len(links) >= 1
    assert any(link["id"] == link_id for link in links)

    # 3. Update the link
    update_data = {
        "title": "Updated Quantum Paper"
    }
    response = await async_client.put(
        f"/api/v1/workspaces/{workspace_id}/research/{link_id}",
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Quantum Paper"

    # 4. Delete the link
    response = await async_client.delete(
        f"/api/v1/workspaces/{workspace_id}/research/{link_id}"
    )
    assert response.status_code == 204
