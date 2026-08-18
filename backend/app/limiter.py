from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://" if settings.ENVIRONMENT == "development" else settings.REDIS_URL,
    in_memory_fallback_enabled=True,
    swallow_errors=True
)
