import json
import functools
import logging
from typing import Callable, Any
from fastapi import Request
from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)

# Global redis client for caching
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache(expire: int = 60):
    """
    Cache decorator for FastAPI endpoints or Service methods.
    It constructs a cache key based on the function name and its stringified arguments.
    It handles basic JSON serialization of the results.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to build a key
            # Skip 'db' and 'self' and non-serializable args from the key
            key_args = []
            for arg in args:
                if not hasattr(arg, 'execute') and not hasattr(arg, '__dict__'):
                    key_args.append(str(arg))
            
            for k, v in kwargs.items():
                if k not in ['db', 'current_user', 'membership', 'request']:
                    key_args.append(f"{k}:{v}")

            # Include function module and name to avoid collisions
            key = f"cache:{func.__module__}:{func.__name__}:{'-'.join(key_args)}"
            
            try:
                cached = await redis_client.get(key)
                if cached:
                    logger.debug(f"Cache hit for key {key}")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis cache error on get: {e}")
                
            # Execute the function if cache miss
            result = await func(*args, **kwargs)
            
            try:
                # We need to serialize the result. Pydantic models have .model_dump()
                if hasattr(result, 'model_dump'):
                    serializable = result.model_dump(mode='json')
                elif hasattr(result, 'dict'):
                    serializable = result.dict()
                else:
                    serializable = result

                await redis_client.setex(key, expire, json.dumps(serializable))
                logger.debug(f"Cache set for key {key}")
            except Exception as e:
                logger.warning(f"Redis cache error on set: {e}")
                
            return result
        return wrapper
    return decorator
