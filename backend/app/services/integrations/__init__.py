from typing import Dict, Any, Type
from .base import SubmissionProviderAdapter, ExternalSubmissionData
from .devfolio import DevfolioAdapter
from .unstop import UnstopAdapter

class ProviderFactory:
    _providers: Dict[str, Type[SubmissionProviderAdapter]] = {
        "devfolio": DevfolioAdapter,
        "unstop": UnstopAdapter,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str, credentials: Dict[str, Any]) -> SubmissionProviderAdapter:
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown integration provider: {provider_name}")
            
        return provider_class(credentials)

__all__ = [
    "SubmissionProviderAdapter",
    "ExternalSubmissionData",
    "ProviderFactory",
    "DevfolioAdapter",
    "UnstopAdapter"
]
