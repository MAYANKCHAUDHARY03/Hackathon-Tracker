import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.activity import ActivityEvent

async def log_activity(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    safe_edge_metadata: dict | None = None
):
    event = ActivityEvent(
        workspace_id=workspace_id,
        actor_id=user_id,
        project_id=project_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        safe_edge_metadata=safe_edge_metadata
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

async def get_project_activities(db: AsyncSession, workspace_id: uuid.UUID, project_id: uuid.UUID, limit: int = 50):
    stmt = (
        select(ActivityEvent)
        .where(
            ActivityEvent.workspace_id == workspace_id,
            ActivityEvent.project_id == project_id
        )
        .order_by(ActivityEvent.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
