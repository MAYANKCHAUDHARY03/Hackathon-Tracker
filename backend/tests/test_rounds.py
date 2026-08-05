import pytest
from httpx import AsyncClient
import uuid

from tests.test_hackathons import get_token_and_workspace

@pytest.mark.asyncio
async def test_create_round(async_client: AsyncClient):
    headers, workspace_id = await get_token_and_workspace(async_client, "test_round@example.com")

    # Create hackathon
    hackathon_data = {
        "name": "Test Round Hackathon",
        "description": "desc",
        "mode": "online",
        "start_date": "2026-01-01T00:00:00Z",
        "end_date": "2026-01-03T00:00:00Z",
        "registration_deadline": "2025-12-31T00:00:00Z",
        "max_team_size": 4
    }
    headers["X-Workspace-Id"] = workspace_id
    r = await async_client.post(f"/api/v1/workspaces/{workspace_id}/hackathons/", json=hackathon_data, headers=headers)
    assert r.status_code == 201
    hackathon = r.json()
    hackathon_id = hackathon["id"]

    # Create round
    round_data = {
        "name": "Round 1",
        "sequence": 1
    }
    r = await async_client.post(f"/api/v1/hackathons/{hackathon_id}/rounds/", json=round_data, headers=headers)
    assert r.status_code == 200
    new_round = r.json()
    assert new_round["name"] == "Round 1"
    assert new_round["sequence"] == 1
    round_id = new_round["id"]

    # Get rounds
    r = await async_client.get(f"/api/v1/hackathons/{hackathon_id}/rounds/", headers=headers)
    assert r.status_code == 200
    rounds = r.json()
    assert len(rounds) == 1
    assert rounds[0]["id"] == round_id
