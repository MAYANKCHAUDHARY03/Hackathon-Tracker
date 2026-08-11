import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import get_current_user, require_workspace_admin, verify_workspace_access
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from app.models.team import Team
from datetime import datetime, timezone, timedelta

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

mock_user_id = uuid.uuid4()
class MockUser:
    def __init__(self, id, email):
        self.id = id
        self.email = email
        self.full_name = "Test User"
        self.is_active = True

@pytest.fixture
def override_deps():
    def _override_user():
        return MockUser(id=mock_user_id, email="test@test.com")
    def _override_access():
        return True
        
    # Save original overrides
    original_overrides = dict(app.dependency_overrides)
    
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_workspace_admin] = _override_access
    app.dependency_overrides[verify_workspace_access] = _override_access
    yield
    
    # Restore original overrides
    app.dependency_overrides = original_overrides

@pytest.mark.asyncio
async def test_get_events(async_client: AsyncClient, db_session: AsyncSession, override_deps):
    # Setup test workspace
    ws_id = uuid.uuid4()
    ws = Workspace(id=ws_id, name="Test WS", slug="test-ws-1")
    db_session.add(ws)
    await db_session.commit()

    # Fetch events API directly
    res = await async_client.get(
        f"/api/v1/workspaces/{ws_id}/events",
    )
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)

@pytest.mark.asyncio
async def test_project_created_emits_event(async_client: AsyncClient, db_session: AsyncSession, override_deps):
    # Setup test workspace, hackathon, and team
    ws_id = uuid.uuid4()
    ws = Workspace(id=ws_id, name="Test WS", slug="test-ws-2")
    db_session.add(ws)
    
    hack_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    hack = Hackathon(
        id=hack_id, 
        workspace_id=ws_id, 
        name="Test Hack", 
        start_date=now,
        end_date=now + timedelta(days=2),
        registration_deadline=now + timedelta(days=1),
        program_type="hackathon",
        mode="online",
        status="draft"
    )
    db_session.add(hack)

    team_id = uuid.uuid4()
    team = Team(id=team_id, name="Test Team", slug="test-team", workspace_id=ws_id, hackathon_id=hack_id)
    db_session.add(team)
    await db_session.commit()

    # 1. Create a project
    project_data = {
        "name": "Event Driven Project",
        "description": "This should emit an event",
        "repository_url": "https://github.com/event",
        "hackathon_id": str(hack_id)
    }
    res = await async_client.post(
        f"/api/v1/workspaces/{ws_id}/teams/{team_id}/projects",
        json=project_data,
    )
    assert res.status_code == 201
    project_id = res.json()["id"]

    # 2. Query events API
    events_res = await async_client.get(
        f"/api/v1/workspaces/{ws_id}/events",
    )
    assert events_res.status_code == 200
    events = events_res.json()
    
    # 3. Assert project_created event exists
    project_events = [e for e in events if e["event_type"] == "project_created" and e["entity_id"] == project_id]
    assert len(project_events) > 0
    event = project_events[0]
    
    assert event["entity_type"] == "project"
    assert event["metadata_json"]["project_name"] == "Event Driven Project"
    assert event["metadata_json"]["team_id"] == str(team_id)
    assert event["actor_id"] == str(mock_user_id)
