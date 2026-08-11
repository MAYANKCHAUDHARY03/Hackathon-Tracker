import pytest
import uuid
import json
import zipfile
import io
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import get_current_user, require_workspace_admin, verify_workspace_access
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from app.models.project import Project
from datetime import datetime, timedelta

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
        return MockUser(id=mock_user_id, email="test@test.com")
    def _override_access():
        return True
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_workspace_admin] = _override_access
    app.dependency_overrides[verify_workspace_access] = _override_access
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_data_exchange_export(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Data Exchange WS", slug="de-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    hackathon = Hackathon(
        workspace_id=workspace.id,
        name="Exchange Hackathon",
        description="Exchange Desc",
        start_date=datetime.utcnow() + timedelta(days=5),
        end_date=datetime.utcnow() + timedelta(days=12),
        registration_deadline=datetime.utcnow() + timedelta(days=2),
        status="draft"
    )
    db_session.add(hackathon)
    await db_session.flush()
    
    from app.models.team import Team
    team = Team(
        workspace_id=workspace.id,
        hackathon_id=hackathon.id,
        name="Exchange Team",
        slug="exchange-team"
    )
    db_session.add(team)
    await db_session.flush()

    project = Project(
        workspace_id=workspace.id,
        hackathon_id=hackathon.id,
        team_id=team.id,
        title="Exchange Project",
        slug="exchange-project",
        solution_summary="Test",
        status="idea"
    )
    db_session.add(project)
    
    await db_session.commit()
    await db_session.refresh(hackathon)
    await db_session.refresh(project)
    
    # Generate API key
    headers = {"Authorization": "Bearer fake_token"}
    payload = {
        "name": "Export API Key",
        "scopes": ["hackathons:read"]
    }
    
    resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/api-keys",
        headers=headers,
        json=payload
    )
    assert resp.status_code == 201
    raw_key = resp.json()["key"]
    
    public_headers = {"X-API-Key": raw_key}
    
    # Test JSON Export
    resp_json = await async_client.get(
        "/api/v1/exchange/export?format=json",
        headers=public_headers
    )
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert data["version"] == "1.0"
    assert len(data["hackathons"]) == 1
    assert data["hackathons"][0]["name"] == "Exchange Hackathon"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "Exchange Project"
    
    # Test NDJSON Export
    resp_ndjson = await async_client.get(
        "/api/v1/exchange/export?format=ndjson",
        headers=public_headers
    )
    assert resp_ndjson.status_code == 200
    lines = resp_ndjson.text.strip().split("\n")
    assert len(lines) == 2
    types = [json.loads(line)["type"] for line in lines]
    assert "hackathon" in types
    assert "project" in types

    # Test CSV Export
    resp_csv = await async_client.get(
        "/api/v1/exchange/export?format=csv",
        headers=public_headers
    )
    assert resp_csv.status_code == 200
    assert resp_csv.headers["content-type"] == "application/zip"
    
    zip_data = io.BytesIO(resp_csv.content)
    with zipfile.ZipFile(zip_data, "r") as zf:
        names = zf.namelist()
        assert "hackathons.csv" in names
        assert "projects.csv" in names
        
        h_csv = zf.read("hackathons.csv").decode("utf-8")
        assert "Exchange Hackathon" in h_csv
