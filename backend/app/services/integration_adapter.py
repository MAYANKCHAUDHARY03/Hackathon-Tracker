import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseIntegrationAdapter(ABC):
    """
    Abstract base class for all integration connectors.
    Enforces a standard contract for authentication and execution.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def test_connection(self) -> bool:
        pass

    @abstractmethod
    async def execute_action(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class SlackAdapter(BaseIntegrationAdapter):
    async def test_connection(self) -> bool:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False
        # In a real scenario, we might hit an auth endpoint. With webhooks, we assume it's valid if present.
        return True

    async def execute_action(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("Slack webhook URL not configured")
            
        if action_type == "send_message":
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json={"text": payload.get("text", "")})
                response.raise_for_status()
                return {"status": "success", "response": response.text}
        
        raise ValueError(f"Unsupported action_type: {action_type}")

class JiraAdapter(BaseIntegrationAdapter):
    async def test_connection(self) -> bool:
        return bool(self.config.get("api_key") and self.config.get("domain"))
        
    async def execute_action(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action_type == "create_issue":
            return {"status": "success", "issue_id": "JIRA-123"} # Mocked
        raise ValueError(f"Unsupported action_type: {action_type}")

# Factory
class IntegrationManager:
    _adapters = {
        "slack": SlackAdapter,
        "jira": JiraAdapter,
        # others...
    }

    @classmethod
    def get_adapter(cls, connector_id: str, config: Dict[str, Any]) -> BaseIntegrationAdapter:
        adapter_cls = cls._adapters.get(connector_id)
        if not adapter_cls:
            raise ValueError(f"No adapter found for connector: {connector_id}")
        return adapter_cls(config)
