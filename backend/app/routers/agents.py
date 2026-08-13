from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uuid

from app.database import get_db
from app.schemas.agent import AgentExecutionResult, AgentDefinition, AgentToolCall
from app.core.agent.registry import tool_registry
from app.agents.research_agent import ResearchAgent

router = APIRouter(prefix="/agents", tags=["agents"])

# In a real system, these might be loaded dynamically from the DB or a plugin system
AVAILABLE_AGENTS = {
    "ResearchAgent": ResearchAgent
}

@router.get("", response_model=List[AgentDefinition])
async def list_agents():
    """
    List all available agents and their allowed tools.
    """
    results = []
    # Instantiate with dummy IDs just to get the properties for the definition
    dummy_db = None
    dummy_uuid = uuid.uuid4()
    for name, agent_cls in AVAILABLE_AGENTS.items():
        agent = agent_cls(db=dummy_db, actor_id=dummy_uuid, workspace_id=dummy_uuid)
        results.append(AgentDefinition(
            name=agent.name,
            description=agent.description,
            allowed_tools=agent.allowed_tools
        ))
    return results

@router.post("/{agent_name}/invoke", response_model=AgentExecutionResult)
async def invoke_agent_tool(
    agent_name: str,
    tool_call: AgentToolCall,
    db: AsyncSession = Depends(get_db)
):
    """
    Invoke a specific tool on behalf of an agent (for testing the middleware).
    """
    if agent_name not in AVAILABLE_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    # Dummy actor and workspace for PoC execution
    actor_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    
    agent = AVAILABLE_AGENTS[agent_name](db, actor_id, workspace_id)
    
    # Actually invoke the middleware
    result = await agent.invoke_tool(tool_name=tool_call.tool_name, parameters=tool_call.parameters)
    
    return result
