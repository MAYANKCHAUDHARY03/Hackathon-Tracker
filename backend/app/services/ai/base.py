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
        
    @abstractmethod
    async def extract_search_intent(self, query: str) -> Dict[str, Any]:
        """Extracts intent and entities from a natural language search query."""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generates a semantic embedding vector for the given text."""
        pass

    @abstractmethod
    async def generate_copilot_response(self, query: str, context: str) -> Dict[str, Any]:
        """Generates an answer based on verified context."""
        pass

    @abstractmethod
    async def generate_forecast(self, target_type: str, target_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates a prediction/forecast based on historical and target data."""
        pass
