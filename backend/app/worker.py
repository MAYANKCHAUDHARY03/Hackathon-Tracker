import asyncio
import logging
from arq.connections import RedisSettings
from app.config import settings

logger = logging.getLogger(__name__)

async def process_webhook(ctx, integration_id: str, action_type: str, payload: dict):
    logger.info(f"Processing webhook for integration {integration_id}")
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.integration import WorkspaceIntegration
    from app.services.integration_adapter import IntegrationManager
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(WorkspaceIntegration).where(WorkspaceIntegration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        if integration:
            adapter = IntegrationManager.get_adapter(integration.connector_id, integration.config)
            await adapter.execute_action(action_type, payload)
        else:
            logger.warning(f"Integration {integration_id} not found")

async def startup(ctx):
    logger.info("Starting up Arq background worker...")
    pass

async def shutdown(ctx):
    logger.info("Shutting down Arq background worker...")
    pass

class WorkerSettings:
    functions = [process_webhook]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
