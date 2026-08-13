from typing import Any, Dict, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import AgentExecutionResult
from app.core.agent.middleware import AgentExecutionMiddleware

class BaseAgent:
    name: str = "BaseAgent"
    description: str = "A generic agent"
    allowed_tools: List[str] = []

    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id
        self.middleware = AgentExecutionMiddleware(db, actor_id, workspace_id)

    async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> AgentExecutionResult:
        """
        Executes a tool on behalf of this agent.
        The execution goes through the shared middleware which enforces the allowlist and logs the event.
        """
        return await self.middleware.execute_tool(
            agent_name=self.name,
            allowed_tools=self.allowed_tools,
            tool_name=tool_name,
            parameters=parameters
        )
