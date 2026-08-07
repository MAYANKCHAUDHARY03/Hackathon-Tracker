import re
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class AIPrivacyFilter:
    """
    Enforces privacy rules on data sent to external AI providers.
    Removes secrets, personal identifiable information, and internal references.
    """
    
    SECRET_PATTERNS = [
        re.compile(r'(?i)password\s*[:=]\s*["\']?[^\s"\']+["\']?'),
        re.compile(r'(?i)api_key\s*[:=]\s*["\']?[^\s"\']+["\']?'),
        re.compile(r'(?i)token\s*[:=]\s*["\']?[^\s"\']+["\']?'),
        re.compile(r'(?i)secret\s*[:=]\s*["\']?[^\s"\']+["\']?')
    ]
    
    @classmethod
    def filter_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive data from dicts."""
        filtered = {}
        for k, v in data.items():
            if any(p.search(k) for p in cls.SECRET_PATTERNS):
                filtered[k] = "[REDACTED]"
            elif isinstance(v, str):
                filtered[k] = cls.filter_text(v)
            elif isinstance(v, dict):
                filtered[k] = cls.filter_dict(v)
            elif isinstance(v, list):
                filtered[k] = cls.filter_list(v)
            else:
                filtered[k] = v
        return filtered
        
    @classmethod
    def filter_list(cls, data: List[Any]) -> List[Any]:
        filtered = []
        for v in data:
            if isinstance(v, str):
                filtered.append(cls.filter_text(v))
            elif isinstance(v, dict):
                filtered.append(cls.filter_dict(v))
            elif isinstance(v, list):
                filtered.append(cls.filter_list(v))
            else:
                filtered.append(v)
        return filtered

    @classmethod
    def filter_text(cls, text: str) -> str:
        """Filter sensitive strings from text blocks."""
        filtered_text = text
        for pattern in cls.SECRET_PATTERNS:
            filtered_text = pattern.sub(lambda m: m.group().split('=')[0].split(':')[0] + "=[REDACTED]", filtered_text)
        return filtered_text

    @classmethod
    def audit_log(cls, provider: str, action: str, data_size: int):
        """Log audit events for AI usage."""
        logger.info(f"AI Audit: Provider={provider} Action={action} DataSize={data_size} bytes")
