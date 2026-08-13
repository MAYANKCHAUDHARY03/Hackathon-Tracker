from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List

from app.models.audit import AuditLog
from app.schemas.audit import AuditLogCreate
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventType

class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(self, log_data: AuditLogCreate) -> AuditLog:
        db_log = AuditLog(**log_data.model_dump())
        self.session.add(db_log)
        await self.session.commit()
        await self.session.refresh(db_log)
        
        # Publish to Canonical Event Stream (Phase 47)
        event_svc = EventService(self.session)
        await event_svc.publish(EventCreate(
            workspace_id=log_data.workspace_id,
            actor_id=log_data.actor_id,
            entity_type=log_data.resource_type,
            entity_id=log_data.resource_id,
            event_type=EventType.AUDIT_LOG,
            source="audit_service",
            metadata_json={
                "action": log_data.action,
                "ip_address": log_data.ip_address,
                "user_agent": log_data.user_agent,
                "status": log_data.status,
                **(log_data.details or {})
            }
        ))
        await self.session.commit()
        
        return db_log

    async def get_logs(self, workspace_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[AuditLog], int]:
        stmt = select(AuditLog).where(AuditLog.workspace_id == workspace_id).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        logs = result.scalars().all()
        
        count_stmt = select(func.count()).select_from(AuditLog).where(AuditLog.workspace_id == workspace_id)
        total = await self.session.scalar(count_stmt)
        
        return list(logs), total or 0
