from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ToolDefinition(BaseModel):
    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)

class AgentToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    agent_name: str

class AgentExecutionResult(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    event_id: Optional[str] = None

class AgentDefinition(BaseModel):
    name: str
    description: str
    allowed_tools: List[str]
