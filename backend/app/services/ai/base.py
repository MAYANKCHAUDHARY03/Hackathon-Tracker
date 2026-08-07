import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AIProviderAdapter(ABC):
    """
    Abstract base class for all AI providers.
    Provides generic methods to generate insights and summaries.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    @abstractmethod
    async def generate_project_summary(self, project_data: Dict[str, Any]) -> str:
        pass
        
    @abstractmethod
    async def analyze_project_health(self, project_data: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Returns health insights and risk scores."""
        pass
