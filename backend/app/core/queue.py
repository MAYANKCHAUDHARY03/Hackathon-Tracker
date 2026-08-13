from arq import create_pool
from arq.connections import RedisSettings
from app.config import settings

redis_pool = None

async def init_queue():
    global redis_pool
    if redis_pool is None:
        redis_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))

async def get_queue():
    if redis_pool is None:
        await init_queue()
    return redis_pool
