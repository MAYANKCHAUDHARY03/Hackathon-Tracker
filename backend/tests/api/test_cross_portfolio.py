import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import verify_workspace_access, require_workspace_admin
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.project import Project

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
    app.dependency_overrides[verify_workspace_access] = _override_user
    app.dependency_overrides[require_workspace_admin] = _override_access
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_cross_portfolio_flow(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Portfolio WS", slug="portfolio-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    from app.models.hackathon import Hackathon
    from app.models.team import Team
    from datetime import datetime, UTC
    
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
    
    t = Team(workspace_id=workspace.id, hackathon_id=h.id, name="Test Team", slug="test-team")
    db_session.add(t)
    await db_session.commit()
    await db_session.refresh(t)

    # Create Project 1
    p1 = Project(workspace_id=workspace.id, hackathon_id=h.id, team_id=t.id, title="Project Alpha", slug="project-alpha", description="A", created_by=uuid.uuid4())
    db_session.add(p1)
    await db_session.commit()
    await db_session.refresh(p1)

    # 1. Create Portfolio
    resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/portfolios",
        json={
            "title": "My Super Portfolio",
            "description": "Showcase of my best projects",
            "is_public": True
        }
    )
    assert resp.status_code == 201
    portfolio_data = resp.json()
    portfolio_id = portfolio_data["id"]
    assert portfolio_data["title"] == "My Super Portfolio"
    assert portfolio_data["owner_id"] == str(mock_user_id)

    # 2. List Portfolios
    list_resp = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/portfolios"
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # 3. Add Project to Portfolio
    add_resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/portfolios/{portfolio_id}/projects",
        json={"project_id": str(p1.id)}
    )
    assert add_resp.status_code == 200
    updated_pf = add_resp.json()
    assert len(updated_pf["projects"]) == 1
    assert updated_pf["projects"][0]["name"] == "Project Alpha"
