from typing import List, Dict, Any
from app.core.agent.base import BaseAgent
from app.core.agent.registry import tool_registry
from app.schemas.agent import RiskLevel

# Register some tools for the Research Agent
@tool_registry.register(
    name="search_projects",
    description="Search for existing projects or documents.",
    risk_level=RiskLevel.LOW,
    parameters_schema={
        "query": "string"
    }
)
async def search_projects(query: str) -> List[Dict[str, Any]]:
    # Mock implementation for proof-of-concept
    return [{"title": f"Result for {query}", "content": "Some mock content"}]

@tool_registry.register(
    name="drop_database",
    description="Drop a database (mock).",
    risk_level=RiskLevel.CRITICAL,
    parameters_schema={
        "db_name": "string"
    }
)
async def drop_database(db_name: str) -> bool:
    # High risk tool for testing Phase 48 blocking logic
    return True

class ResearchAgent(BaseAgent):
    name: str = "ResearchAgent"
    description: str = "An agent that researches topics across projects."
    allowed_tools: List[str] = ["search_projects"]
