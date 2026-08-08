import pytest
import uuid
from httpx import AsyncClient
from app.models.graph import GraphEdge
from app.models.user import User, WorkspaceMembership
from app.dependencies import verify_workspace_access, get_current_user
from app.main import app

async def override_verify_workspace_access():
    return WorkspaceMembership(id=uuid.uuid4(), workspace_id=uuid.uuid4(), user_id=uuid.uuid4(), role="admin")

async def override_get_current_user():
    return User(id=uuid.uuid4(), email="test@test.com")

app.dependency_overrides[verify_workspace_access] = override_verify_workspace_access
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.mark.asyncio
async def test_graph_edge_creation(async_client: AsyncClient):
    workspace_id = str(uuid.uuid4())
    
    edge_data = {
        "source_type": "Hackathon",
        "source_id": str(uuid.uuid4()),
        "target_type": "Challenge",
        "target_id": str(uuid.uuid4()),
        "relation_type": "contains",
        "properties": {"weight": 1.0}
    }
    
    response = await async_client.post(f"/api/v1/workspaces/{workspace_id}/graph/edges", json=edge_data)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "Hackathon"
    assert data["relation_type"] == "contains"

@pytest.mark.asyncio
async def test_graph_traversal(async_client: AsyncClient):
    workspace_id = str(uuid.uuid4())
    source_id = str(uuid.uuid4())
    target_id = str(uuid.uuid4())
    
    edge_data = {
        "source_type": "Team",
        "source_id": source_id,
        "target_type": "Project",
        "target_id": target_id,
        "relation_type": "created",
        "properties": {}
    }
    
    await async_client.post(f"/api/v1/workspaces/{workspace_id}/graph/edges", json=edge_data)
    
    response = await async_client.get(f"/api/v1/workspaces/{workspace_id}/graph/traverse/{source_id}?depth=2")
    assert response.status_code == 200
    data = response.json()
    
    assert "path" in data
    assert "nodes" in data
    assert len(data["path"]) >= 1
    edge_found = any(e["source_id"] == source_id and e["target_id"] == target_id for e in data["path"])
    assert edge_found
