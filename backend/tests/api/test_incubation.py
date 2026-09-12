import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from app.models.team import Team
from app.models.project import Project

@pytest.fixture(autouse=True)
def override_deps():
    async def override_get_current_user():
        return User(id=uuid.uuid4(), email="test@test.com")
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer testtoken"}

@pytest.mark.asyncio
async def test_incubation_dashboard(
    async_client: AsyncClient,
    auth_headers,
    db_session: AsyncSession
):
    # Setup using ORM models (respects defaults and NOT NULL constraints)
    now = datetime.now(timezone.utc)
    
    workspace = Workspace(name="Test Workspace", slug=f"test-{uuid.uuid4()}", settings={})
    db_session.add(workspace)
    await db_session.flush()
    
    hackathon = Hackathon(
        workspace_id=workspace.id, name="Test Hackathon",
        registration_deadline=now, start_date=now, end_date=now
    )
    db_session.add(hackathon)
    await db_session.flush()
    
    team = Team(
        workspace_id=workspace.id, hackathon_id=hackathon.id,
        name="Test Team", slug=f"test-team-{uuid.uuid4()}"
    )
    db_session.add(team)
    await db_session.flush()
    
    project = Project(
        workspace_id=workspace.id, hackathon_id=hackathon.id,
        team_id=team.id, title="Test Project",
        slug=f"test-proj-{uuid.uuid4()}", status="INCUBATION"
    )
    db_session.add(project)
    await db_session.commit()

    # 1. Create an update
    response = await async_client.post(
        f"/api/v1/projects/{project.id}/incubation/updates",
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
        f"/api/v1/projects/{project.id}/incubation/funding",
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
        f"/api/v1/projects/{project.id}/incubation/dashboard",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["updates"]) == 1
    assert len(data["funding_rounds"]) == 1
    assert len(data["documents"]) == 0
    assert len(data["stakeholders"]) == 0
