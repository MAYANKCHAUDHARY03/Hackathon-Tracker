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
async def test_ask_copilot(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Copilot WS", slug="copilot-ws", organization_id=uuid.uuid4())
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
    
    t = Team(workspace_id=workspace.id, hackathon_id=h.id, name="Test Team", slug="test-team-2")
    db_session.add(t)
    await db_session.commit()
    await db_session.refresh(t)

    # Setup test project for context
    project = Project(
        workspace_id=workspace.id,
        hackathon_id=h.id,
        team_id=t.id,
        title="AI Medical Assistant",
        slug="ai-medical-assistant",
        description="A medical tool using computer vision.",
        created_by=uuid.uuid4()
    )
    db_session.add(project)
    await db_session.commit()
    
    # Payload for the copilot query
    payload = {
        "query": "Tell me about the medical project."
    }
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/copilot/ask",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "evidence" in data
    assert "source_entities" in data
    assert "confidence" in data
    
    # Because of mock provider, it should contain a mock response or fallback string.
    assert isinstance(data["source_entities"], list)
