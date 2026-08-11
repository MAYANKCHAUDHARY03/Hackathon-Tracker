import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.dependencies import verify_workspace_access, require_workspace_admin
from tests.conftest import TestingSessionLocal
from app.models.workspace import Workspace
from app.models.matchmaking import MatchOpportunity, MatchProfile, MatchRecommendation

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
async def test_matchmaking_flow(
    async_client: AsyncClient, 
    db_session: AsyncSession,
    override_deps
):
    workspace = Workspace(name="Match WS", slug="match-ws", organization_id=uuid.uuid4())
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # 1. Create Profile
    entity_id = str(uuid.uuid4())
    resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/matchmaking/profiles",
        json={
            "entity_type": "startup",
            "entity_id": entity_id,
            "tags": ["AI", "Fintech"],
            "needs": ["Funding"]
        }
    )
    assert resp.status_code == 201
    profile_data = resp.json()
    profile_id = profile_data["id"]
    assert profile_data["tags"] == ["AI", "Fintech"]

    # 2. Create Opportunity
    opp_resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/matchmaking/opportunities",
        json={
            "title": "Seed Fund",
            "opportunity_type": "investor",
            "tags": ["fintech", "b2b"]
        }
    )
    assert opp_resp.status_code == 201
    opp_data = opp_resp.json()
    assert opp_data["title"] == "Seed Fund"

    # 3. List Opportunities
    list_resp = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/matchmaking/opportunities"
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # 4. Generate Recommendations
    rec_resp = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/matchmaking/profiles/{profile_id}/recommendations"
    )
    assert rec_resp.status_code == 200
    recs = rec_resp.json()
    assert len(recs) == 1
    # Check score calculation (Fintech overlap -> 20)
    assert recs[0]["score"] == 20
    assert recs[0]["opportunity"]["title"] == "Seed Fund"
