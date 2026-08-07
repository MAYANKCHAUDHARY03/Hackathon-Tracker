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

@pytest.mark.asyncio
async def test_get_dashboard_summary_empty(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "dash_empty@example.com")
    
    response = await async_client.get(
        f"/api/v1/workspaces/{workspace_id}/dashboard",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_active"] == 0
    assert data["total_upcoming"] == 0
    assert data["total_completed"] == 0
    assert data["total_non_archived"] == 0
    assert len(data["upcoming_deadlines"]) == 0
    assert data["nearest_upcoming_event"] is None
    assert len(data["recently_updated"]) == 0

@pytest.mark.asyncio
async def test_get_dashboard_summary_populated(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "dash_pop@example.com")
    now = datetime.now(timezone.utc)
    
    # 1. Active Hackathon
    await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons",
        json={
            "name": "Active Hackathon",
            "mode": "online",
            "start_date": (now - timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=2)).isoformat(),
            "registration_deadline": (now - timedelta(days=2)).isoformat()
        },
        headers=headers
    )

    # 2. Upcoming Hackathon
    await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons",
        json={
            "name": "Upcoming Hackathon",
            "mode": "online",
            "start_date": (now + timedelta(days=5)).isoformat(),
            "end_date": (now + timedelta(days=7)).isoformat(),
            "registration_deadline": (now + timedelta(days=3)).isoformat()
        },
        headers=headers
    )

    # 3. Completed Hackathon
    await async_client.post(
        f"/api/v1/workspaces/{workspace_id}/hackathons",
        json={
            "name": "Completed Hackathon",
            "mode": "online",
            "start_date": (now - timedelta(days=10)).isoformat(),
            "end_date": (now - timedelta(days=8)).isoformat(),
            "registration_deadline": (now - timedelta(days=11)).isoformat()
        },
        headers=headers
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace_id}/dashboard",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_non_archived"] >= 3
    assert data["total_active"] >= 1
    assert data["total_upcoming"] >= 1
    assert data["total_completed"] >= 1

    assert data["nearest_upcoming_event"]["name"] == "Upcoming Hackathon"
    assert len(data["recently_updated"]) >= 3
    assert len(data["upcoming_deadlines"]) >= 2  # Active and Upcoming ones
