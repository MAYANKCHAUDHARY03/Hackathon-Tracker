import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_high_risk_tool_creates_approval(async_client: AsyncClient):
    """
    Test that a CRITICAL risk tool creates an approval request and doesn't execute immediately.
    """
    payload = {
        "tool_name": "drop_database",
        "parameters": {"db_name": "test_db"},
        "agent_name": "ResearchAgent"
    }
    
    response = await async_client.post("/api/v1/agents/ResearchAgent/invoke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_approval"
    assert "approval_id" in data
    
    # 2. Get the approval
    approval_id = data["approval_id"]
    response = await async_client.get("/api/v1/approvals")
    assert response.status_code == 200
    approvals = response.json()
    
    found = False
    for app in approvals:
        if app["id"] == approval_id:
            found = True
            assert app["status"] == "pending"
    assert found

    # 3. Approve it
    response = await async_client.post(f"/api/v1/approvals/{approval_id}/approve")
    assert response.status_code == 200
    approve_data = response.json()
    assert approve_data["status"] == "success"
    assert approve_data["result"] is True # drop_database mock returns True
