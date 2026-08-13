from typing import Dict, Optional, Callable, Any
from app.schemas.agent import ToolDefinition, RiskLevel

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}

    def register(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel = RiskLevel.LOW,
        parameters_schema: Optional[Dict[str, Any]] = None
    ):
        def decorator(func: Callable[..., Any]):
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                risk_level=risk_level,
                parameters_schema=parameters_schema or {}
            )
            self._handlers[name] = func
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def get_handler(self, name: str) -> Optional[Callable[..., Any]]:
        return self._handlers.get(name)

    def list_tools(self) -> Dict[str, ToolDefinition]:
        return self._tools.copy()

# Global registry instance
tool_registry = ToolRegistry()
