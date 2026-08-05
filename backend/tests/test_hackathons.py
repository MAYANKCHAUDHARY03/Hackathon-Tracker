import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone

async def get_token_and_workspace(async_client: AsyncClient, email: str, full_name: str = "Test User"):
    # Register
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": "password123"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get workspace
    ws_response = await async_client.get("/api/v1/workspaces", headers=headers)
    workspace_id = ws_response.json()[0]["id"]
    
    return headers, workspace_id

@pytest.fixture
def valid_hackathon_data():
    now = datetime.now(timezone.utc)
    start = now + timedelta(days=10)
    end = start + timedelta(days=2)
    reg = start - timedelta(days=1)
    
    return {
        "name": "Super Hackathon",
        "description": "A great event",
        "mode": "online",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "registration_deadline": reg.isoformat(),
        "max_team_size": 4
    }

@pytest.mark.asyncio
async def test_create_hackathon(async_client: AsyncClient, valid_hackathon_data):
    headers, workspace_id = await get_token_and_workspace(async_client, "owner@example.com")
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons/",
        json=valid_hackathon_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Super Hackathon"
    assert data["workspace_id"] == workspace_id
    assert data["status"] == "draft"

@pytest.mark.asyncio
async def test_unauthenticated_create(async_client: AsyncClient, valid_hackathon_data):
    # Register just to get a valid workspace ID
    _, workspace_id = await get_token_and_workspace(async_client, "anon@example.com")
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons/",
        json=valid_hackathon_data
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_invalid_date_order(async_client: AsyncClient, valid_hackathon_data):
    headers, workspace_id = await get_token_and_workspace(async_client, "dates@example.com")
    
    invalid_data = valid_hackathon_data.copy()
    invalid_data["end_date"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons/",
        json=invalid_data,
        headers=headers
    )
    assert response.status_code == 422
    assert "end_date cannot be earlier than start_date" in response.text

@pytest.mark.asyncio
async def test_invalid_url(async_client: AsyncClient, valid_hackathon_data):
    headers, workspace_id = await get_token_and_workspace(async_client, "url@example.com")
    
    invalid_data = valid_hackathon_data.copy()
    invalid_data["official_url"] = "not-a-url"
    
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons/",
        json=invalid_data,
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_and_retrieve(async_client: AsyncClient, valid_hackathon_data):
    headers, workspace_id = await get_token_and_workspace(async_client, "list@example.com")
    
    # Create
    resp1 = await async_client.post(f"/api/v1/workspaces/{workspace_id}/hackathons/", json=valid_hackathon_data, headers=headers)
    h_id = resp1.json()["id"]
    
    # Retrieve
    get_resp = await async_client.get(f"/api/v1/workspaces/{workspace_id}/hackathons/{h_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == h_id
    
    # List
    list_resp = await async_client.get(f"/api/v1/workspaces/{workspace_id}/hackathons/", headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

@pytest.mark.asyncio
async def test_workspace_isolation(async_client: AsyncClient, valid_hackathon_data):
    # User A
    headers_a, workspace_id_a = await get_token_and_workspace(async_client, "usera@example.com")
    resp_a = await async_client.post(f"/api/v1/workspaces/{workspace_id_a}/hackathons/", json=valid_hackathon_data, headers=headers_a)
    hackathon_id_a = resp_a.json()["id"]
    
    # User B
    headers_b, workspace_id_b = await get_token_and_workspace(async_client, "userb@example.com")
    
    # User B tries to access User A's hackathon in User A's workspace
    bad_req1 = await async_client.get(f"/api/v1/workspaces/{workspace_id_a}/hackathons/{hackathon_id_a}", headers=headers_b)
    assert bad_req1.status_code in (404, 403)
    
    # User B tries to access User A's hackathon guessing UUID in their own workspace
    bad_req2 = await async_client.get(f"/api/v1/workspaces/{workspace_id_b}/hackathons/{hackathon_id_a}", headers=headers_b)
    assert bad_req2.status_code == 404

@pytest.mark.asyncio
async def test_update_hackathon(async_client: AsyncClient, valid_hackathon_data):
    headers, workspace_id = await get_token_and_workspace(async_client, "update@example.com")
    resp = await async_client.post(f"/api/v1/workspaces/{workspace_id}/hackathons/", json=valid_hackathon_data, headers=headers)
    h_id = resp.json()["id"]
    
    update_resp = await async_client.put(
        f"/api/v1/workspaces/{workspace_id}/hackathons/{h_id}",
        json={"name": "Updated Name"},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_archive_restore_delete(async_client: AsyncClient, valid_hackathon_data):
    headers, workspace_id = await get_token_and_workspace(async_client, "ard@example.com")
    resp = await async_client.post(f"/api/v1/workspaces/{workspace_id}/hackathons/", json=valid_hackathon_data, headers=headers)
    h_id = resp.json()["id"]
    
    # Archive
    archive_resp = await async_client.post(f"/api/v1/workspaces/{workspace_id}/hackathons/{h_id}/archive", headers=headers)
    assert archive_resp.status_code == 200
    assert archive_resp.json()["status"] == "archived"
    
    # Excluded from list by default
    list_resp1 = await async_client.get(f"/api/v1/workspaces/{workspace_id}/hackathons/", headers=headers)
    assert list_resp1.json()["total"] == 0
    
    # Included if requested
    list_resp2 = await async_client.get(f"/api/v1/workspaces/{workspace_id}/hackathons/?include_archived=true", headers=headers)
    assert list_resp2.json()["total"] == 1
    
    # Restore
    restore_resp = await async_client.post(f"/api/v1/workspaces/{workspace_id}/hackathons/{h_id}/restore", headers=headers)
    assert restore_resp.status_code == 200
    assert restore_resp.json()["status"] == "draft"
    
    # Delete
    del_resp = await async_client.delete(f"/api/v1/workspaces/{workspace_id}/hackathons/{h_id}", headers=headers)
    assert del_resp.status_code == 204
    
    # Gone
    get_resp = await async_client.get(f"/api/v1/workspaces/{workspace_id}/hackathons/{h_id}", headers=headers)
    assert get_resp.status_code == 404
