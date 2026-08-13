import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.activity import ActivityEvent
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventType

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
    # 1. Write to legacy activity table (per user feedback)
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
    
    # 2. Publish to Canonical Event Stream (Phase 47)
    event_svc = EventService(db)
    
    # Map Kanban action to generic event_type
    canonical_event_type = EventType.GENERAL_ACTIVITY
    if entity_type == "KanbanTask" and action == "moved":
        canonical_event_type = EventType.TASK_COMPLETED # Or task_moved, but we'll use TASK_COMPLETED mapping for now if it hits Done. Let's just use general Activity if not explicit
    
    await event_svc.publish(EventCreate(
        workspace_id=workspace_id,
        actor_id=user_id,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        event_type=canonical_event_type,
        source="activity_service",
        metadata_json={
            "action": action,
            "project_id": str(project_id) if project_id else None,
            **(safe_edge_metadata or {})
        }
    ))
    
    # We do not commit again here because EventService.publish will just flush, 
    # but wait, EventService.publish relies on the caller to commit if we want it persisted.
    await db.commit()

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
