import uuid
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.schemas.agent import AgentExecutionResult, RiskLevel
from app.core.agent.registry import tool_registry
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventType

class AgentExecutionMiddleware:
    """
    Core middleware that intercepts every tool call from an agent.
    Enforces isolation, risk-level blocking, and logging.
    """
    
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id
        self.event_service = EventService(db)

    async def execute_tool(self, agent_name: str, allowed_tools: list[str], tool_name: str, parameters: Dict[str, Any]) -> AgentExecutionResult:
        # 1. Enforce Tool Allowlist
        if tool_name not in allowed_tools:
            return AgentExecutionResult(
                status="error",
                error=f"PermissionDenied: Tool '{tool_name}' is not in the allow-list for agent '{agent_name}'."
            )
            
        tool_def = tool_registry.get_tool(tool_name)
        if not tool_def:
            return AgentExecutionResult(
                status="error",
                error=f"NotFoundError: Tool '{tool_name}' is not registered globally."
            )
            
        # 2. Risk Level Blocking (Phase 48 Rule: Block High/Critical until Phase 49)
        if tool_def.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return AgentExecutionResult(
                status="error",
                error=f"Blocked: Tool '{tool_name}' is classified as {tool_def.risk_level.value} risk. Phase 49 Human Approval Framework is required."
            )
            
        # 3. Execution
        handler = tool_registry.get_handler(tool_name)
        try:
            # We assume handlers are async
            result = await handler(**parameters)
            status = "success"
            error = None
        except Exception as e:
            result = None
            status = "error"
            error = str(e)
            
        # 4. Logging & Traceability (Phase 47 Canonical Stream)
        event_create = EventCreate(
            workspace_id=self.workspace_id,
            actor_id=self.actor_id,
            entity_type="Agent",
            entity_id=agent_name,
            event_type=EventType.GENERAL_ACTIVITY,
            source="agent_framework",
            metadata_json={
                "tool_name": tool_name,
                "parameters": parameters,
                "status": status,
                "error": error
            }
        )
        await self.event_service.publish(event_create)
        
        # We explicitly commit to ensure the audit trail is saved
        await self.db.commit()
        
        return AgentExecutionResult(
            status=status,
            result=result,
            error=error
        )
