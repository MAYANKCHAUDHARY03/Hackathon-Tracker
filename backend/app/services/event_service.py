from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.event import PlatformEvent
from app.schemas.event import EventCreate
from app.core.event_bus import event_bus

class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def publish(self, event_in: EventCreate) -> PlatformEvent:
        # Create database record
        db_event = PlatformEvent(
            workspace_id=event_in.workspace_id,
            actor_id=event_in.actor_id,
            entity_type=event_in.entity_type,
            entity_id=event_in.entity_id,
            event_type=event_in.event_type,
            source=event_in.source,
            correlation_id=event_in.correlation_id,
            metadata_json=event_in.metadata_json or {}
        )
        self.session.add(db_event)
        # Flush to get the ID and timestamp assigned, but don't commit yet to keep it in the current transaction
        await self.session.flush()
        
        # Publish to the in-memory event bus for downstream async workers/subscribers
        # We pass the db_event directly (or we could pass a dict schema)
        await event_bus.publish(event_in.event_type, db_event)
        
        return db_event

    async def get_events(self, workspace_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[PlatformEvent]:
        stmt = select(PlatformEvent).where(PlatformEvent.workspace_id == workspace_id).order_by(PlatformEvent.timestamp.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
