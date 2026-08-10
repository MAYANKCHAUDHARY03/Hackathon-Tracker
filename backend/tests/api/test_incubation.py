import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.main import app
from app.dependencies import get_current_user
from app.models.user import User

async def override_get_current_user():
    return User(id=uuid.uuid4(), email="test@test.com")

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer testtoken"}

@pytest.fixture
async def db_session():
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as session:
        yield session

@pytest.mark.asyncio
async def test_incubation_dashboard(
    async_client: AsyncClient,
    auth_headers,
    db_session: AsyncSession
):
    # Setup - mock project and workspace
    workspace_id = uuid.uuid4()
    project_id = uuid.uuid4()
    hackathon_id = uuid.uuid4()
    team_id = uuid.uuid4()

    await db_session.execute(text(
        "INSERT INTO workspaces (id, name, slug) VALUES (:id, :name, :slug)"
    ), {"id": str(workspace_id), "name": "Test Workspace", "slug": f"test-{workspace_id}"})
    
    await db_session.execute(text(
        "INSERT INTO hackathons (id, workspace_id, name, slug) VALUES (:id, :ws_id, :name, :slug)"
    ), {"id": str(hackathon_id), "ws_id": str(workspace_id), "name": "Test Hackathon", "slug": f"test-hack-{hackathon_id}"})
    
    await db_session.execute(text(
        "INSERT INTO teams (id, workspace_id, hackathon_id, name) VALUES (:id, :ws_id, :h_id, :name)"
    ), {"id": str(team_id), "ws_id": str(workspace_id), "h_id": str(hackathon_id), "name": "Test Team"})
    
    await db_session.execute(text(
        "INSERT INTO projects (id, workspace_id, hackathon_id, team_id, title, slug, status) VALUES (:id, :ws_id, :h_id, :t_id, :title, :slug, :status)"
    ), {"id": str(project_id), "ws_id": str(workspace_id), "h_id": str(hackathon_id), "t_id": str(team_id), "title": "Test Project", "slug": f"test-proj-{project_id}", "status": "INCUBATION"})
    
    await db_session.commit()

    # 1. Create an update
    response = await async_client.post(
        f"/api/v1/projects/{project_id}/incubation/updates",
        headers=auth_headers,
        json={
            "title": "August Update",
            "content": "Things are going well.",
            "update_type": "progress_report"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "August Update"

    # 2. Add funding
    response = await async_client.post(
        f"/api/v1/projects/{project_id}/incubation/funding",
        headers=auth_headers,
        json={
            "round_type": "pre_seed",
            "amount": 500000.0,
            "currency": "USD",
            "date": "2026-08-10T00:00:00Z"
        }
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 500000.0

    # 3. Fetch dashboard
    response = await async_client.get(
        f"/api/v1/projects/{project_id}/incubation/dashboard",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["updates"]) == 1
    assert len(data["funding_rounds"]) == 1
    assert len(data["documents"]) == 0
    assert len(data["stakeholders"]) == 0
