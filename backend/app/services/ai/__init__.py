from typing import Dict, Any
from .base import AIProviderAdapter
from .providers import MockAIProvider
from .privacy import AIPrivacyFilter

class AIProviderFactory:
    @classmethod
    def get_provider(cls, provider_name: str, api_key: str) -> AIProviderAdapter:
        if provider_name.lower() == "mock":
            return MockAIProvider(api_key)
        # We can add actual providers here like OpenAI, Anthropic, Gemini
        # but defaulting to mock to prevent arbitrary AI execution during tests
        return MockAIProvider(api_key)

__all__ = [
    "AIProviderAdapter",
    "AIPrivacyFilter",
    "AIProviderFactory"
]
