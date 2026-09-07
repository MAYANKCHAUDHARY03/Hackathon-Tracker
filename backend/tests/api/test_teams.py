import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import get_current_user, require_workspace_admin, verify_workspace_access
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from datetime import datetime, timezone

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
    
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[verify_workspace_access] = _override_access
    app.dependency_overrides[require_workspace_admin] = _override_access
    
    yield
    
    app.dependency_overrides = {}

@pytest.fixture
async def test_workspace_and_hackathon(db_session: AsyncSession):
    ws_id = uuid.uuid4()
    ws = Workspace(id=ws_id, name="Test WS", slug=f"ws-{ws_id}")
    
    hackathon_id = uuid.uuid4()
    hackathon = Hackathon(
        id=hackathon_id,
        workspace_id=ws_id,
        name="Test Hackathon",
        registration_deadline=datetime.now(timezone.utc),
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc)
    )
    db_session.add_all([ws, hackathon])
    await db_session.commit()
    return ws_id, hackathon_id

async def test_create_team_valid(async_client: AsyncClient, test_workspace_and_hackathon, override_deps):
    ws_id, _ = test_workspace_and_hackathon
    
    payload = {
        "name": "Super Team",
        "description": "We are awesome",
        "skills_needed": ["Python", "React"]
    }
    
    response = await async_client.post(f"/api/v1/workspaces/{ws_id}/teams", json=payload)
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Super Team"
    assert "id" in data

async def test_create_team_missing_name(async_client: AsyncClient, test_workspace_and_hackathon, override_deps):
    ws_id, _ = test_workspace_and_hackathon
    
    payload = {
        "description": "Missing name!"
    }
    
    response = await async_client.post(f"/api/v1/workspaces/{ws_id}/teams", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Ensure it's a list of validation errors
    assert isinstance(data["detail"], list)
    assert data["detail"][0]["loc"][-1] == "name"

