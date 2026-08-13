import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_list_agents(async_client: AsyncClient):
    """
    Test listing available agents.
    """
    response = await async_client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) > 0
    # Check for ResearchAgent
    agent_names = [a["name"] for a in agents]
    assert "ResearchAgent" in agent_names

@pytest.mark.asyncio
async def test_invoke_allowed_tool(async_client: AsyncClient):
    """
    Test invoking a tool that IS in the agent's allow-list (low risk).
    """
    payload = {
        "tool_name": "search_projects",
        "parameters": {"query": "AI Hackathon"},
        "agent_name": "ResearchAgent"
    }
    response = await async_client.post("/api/v1/agents/ResearchAgent/invoke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] is not None
    assert "Result for AI Hackathon" in data["result"][0]["title"]

@pytest.mark.asyncio
async def test_invoke_unallowed_tool(async_client: AsyncClient):
    """
    Test invoking a tool that is NOT in the agent's allow-list.
    """
    payload = {
        "tool_name": "drop_database",
        "parameters": {"db_name": "test"},
        "agent_name": "ResearchAgent"
    }
    response = await async_client.post("/api/v1/agents/ResearchAgent/invoke", json=payload)
    assert response.status_code == 200 # HTTP is successful, but tool fails
    data = response.json()
    assert data["status"] == "error"
    assert "PermissionDenied" in data["error"]
