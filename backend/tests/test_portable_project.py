import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

async def get_token_and_workspace(async_client: AsyncClient, email: str = "portable@test.com"):
    # Register
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Portable User", "password": "password123"}
    )
    if reg_response.status_code != 201:
        # Maybe already exists, let's login
        reg_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "password123"}
        )
    if "access_token" not in reg_response.json():
        raise ValueError(f"Auth failed: {reg_response.status_code} {reg_response.text}")
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get workspace
    ws_response = await async_client.get("/api/v1/workspaces", headers=headers)
    ws_data = ws_response.json()
    if not ws_data:
        new_ws = await async_client.post("/api/v1/workspaces", json={"name": f"Test WS {email}", "slug": f"test-ws-{email.split('@')[0]}"}, headers=headers)
        workspace_id = new_ws.json().get("id")
    else:
        workspace_id = ws_data[0]["id"]
        
    return headers, workspace_id

@pytest.mark.asyncio
async def test_create_portable_identity(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "t1@test.com")
    
    response = await async_client.post(
        "/api/v1/portable-projects",
        headers=headers,
        json={
            "name": "Global AI Network",
            "slug": "global-ai-network",
            "description": "A truly portable project",
            "current_stage": "hackathon",
            "visibility": "public"
        }
    )
    if response.status_code != 201: print(response.text); assert False
    data = response.json()
    assert "id" in data
    assert data["current_stage"] == "hackathon"

@pytest.mark.asyncio
async def test_get_portable_identity(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "t2@test.com")
    
    # Create identity first
    response = await async_client.post(
        "/api/v1/portable-projects",
        headers=headers,
        json={
            "name": "Global AI Network 2",
            "slug": "global-ai-network-2",
            "description": "A truly portable project",
            "current_stage": "hackathon",
            "visibility": "public"
        }
    )
    if response.status_code != 201: print(response.text); assert False
    project_id = response.json()["id"]
    
    # Get identity
    response = await async_client.get(
        f"/api/v1/portable-projects/{project_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_stage"] == "hackathon"

@pytest.mark.asyncio
async def test_record_stage_transition(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "t3@test.com")
    
    # Create identity
    res = await async_client.post(
        "/api/v1/portable-projects",
        headers=headers,
        json={
            "name": "Global AI Network 3",
            "slug": "global-ai-network-3",
            "description": "A truly portable project",
            "current_stage": "hackathon",
            "visibility": "public"
        }
    )
    assert res.status_code == 201
    project_id = res.json()["id"]
    
    transition_data = {
        "to_stage": "incubation",
        "organization_id": workspace_id,
        "program_context_type": "Summer Batch 2026",
        "notes": "Accepted to incubator"
    }
    
    response = await async_client.post(
        f"/api/v1/portable-projects/{project_id}/transitions",
        json=transition_data,
        headers=headers
    )
    if response.status_code != 201: print(response.text); assert False
    data = response.json()
    assert data["to_stage"] == "incubation"
    assert data["from_stage"] == "hackathon"

@pytest.mark.asyncio
async def test_get_transition_history(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "t4@test.com")
    
    # Create identity
    res = await async_client.post(
        "/api/v1/portable-projects",
        headers=headers,
        json={
            "name": "Global AI Network 4",
            "slug": "global-ai-network-4",
            "description": "A truly portable project",
            "current_stage": "hackathon",
            "visibility": "public"
        }
    )
    assert res.status_code == 201
    project_id = res.json()["id"]
    
    # Make a transition
    transition_data = {
        "to_stage": "incubation",
        "organization_id": workspace_id,
        "program_context_type": "Summer Batch 2026",
        "notes": "Accepted to incubator"
    }
    await async_client.post(
        f"/api/v1/portable-projects/{project_id}/transitions",
        json=transition_data,
        headers=headers
    )
    
    # Get history
    response = await async_client.get(
        f"/api/v1/portable-projects/{project_id}/history",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "transitions" in data
    assert len(data["transitions"]) == 2
    assert data["transitions"][0]["to_stage"] == "incubation"
