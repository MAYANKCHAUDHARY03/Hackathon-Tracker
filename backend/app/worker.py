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

async def enforce_data_retention(ctx):
    logger.info("Running data retention sweep...")
    from app.database import AsyncSessionLocal
    from sqlalchemy import select, delete
    from app.models.workspace import Workspace
    from app.models.governance import GovernanceAuditLog
    from datetime import datetime, timezone, timedelta
    
    async with AsyncSessionLocal() as session:
        # Fetch all workspaces to check their policies
        result = await session.execute(select(Workspace))
        workspaces = result.scalars().all()
        
        for ws in workspaces:
            policy = ws.settings.get("governance_policy", {})
            retention_days = policy.get("retention_days", 365)
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            
            # Delete audit logs older than retention_days
            await session.execute(
                delete(GovernanceAuditLog).where(
                    GovernanceAuditLog.workspace_id == ws.id,
                    GovernanceAuditLog.created_at < cutoff_date
                )
            )
        await session.commit()
    logger.info("Data retention sweep completed.")

async def startup(ctx):
    logger.info("Starting up Arq background worker...")
    pass

async def shutdown(ctx):
    logger.info("Shutting down Arq background worker...")
    pass

from arq.cron import cron

class WorkerSettings:
    functions = [process_webhook]
    cron_jobs = [cron(enforce_data_retention, hour=0, minute=0)] # Runs daily at midnight UTC
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
