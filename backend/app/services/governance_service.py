import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.governance import DataSubjectRequest, ConsentRecord, GovernanceAuditLog, DSRStatus
from app.schemas.governance import DSRCreate, ConsentCreate

class GovernanceService:
    @staticmethod
    async def create_dsr(workspace_id: uuid.UUID, user_id: uuid.UUID, data: DSRCreate, db: AsyncSession) -> DataSubjectRequest:
        dsr = DataSubjectRequest(
            workspace_id=workspace_id,
            user_id=user_id,
            request_type=data.request_type,
            details=data.details
        )
        db.add(dsr)
        
        # Log this creation
        audit_log = GovernanceAuditLog(
            workspace_id=workspace_id,
            actor_id=user_id,
            action="dsr_created",
            target_resource="DataSubjectRequest",
            details={"request_type": data.request_type.value}
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(dsr)
        return dsr

    @staticmethod
    async def get_dsrs(workspace_id: uuid.UUID, user_id: Optional[uuid.UUID], db: AsyncSession) -> List[DataSubjectRequest]:
        query = select(DataSubjectRequest).where(DataSubjectRequest.workspace_id == workspace_id)
        if user_id:
            query = query.where(DataSubjectRequest.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_dsr_status(workspace_id: uuid.UUID, dsr_id: uuid.UUID, status: DSRStatus, resolution_notes: str, actor_id: uuid.UUID, db: AsyncSession) -> DataSubjectRequest:
        query = select(DataSubjectRequest).where(
            DataSubjectRequest.id == dsr_id,
            DataSubjectRequest.workspace_id == workspace_id
        )
        result = await db.execute(query)
        dsr = result.scalar_one_or_none()
        if not dsr:
            raise HTTPException(status_code=404, detail="DSR not found")
        
        dsr.status = status
        dsr.resolution_notes = resolution_notes
        if status in [DSRStatus.COMPLETED, DSRStatus.REJECTED]:
            dsr.completed_at = datetime.now(timezone.utc)
            
        audit_log = GovernanceAuditLog(
            workspace_id=workspace_id,
            actor_id=actor_id,
            action="dsr_status_updated",
            target_resource="DataSubjectRequest",
            target_id=str(dsr_id),
            details={"new_status": status.value}
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(dsr)
        return dsr

    @staticmethod
    async def record_consent(workspace_id: uuid.UUID, user_id: uuid.UUID, data: ConsentCreate, ip_address: str, db: AsyncSession) -> ConsentRecord:
        consent = ConsentRecord(
            workspace_id=workspace_id,
            user_id=user_id,
            consent_type=data.consent_type,
            status=data.status,
            ip_address=ip_address
        )
        db.add(consent)
        
        audit_log = GovernanceAuditLog(
            workspace_id=workspace_id,
            actor_id=user_id,
            action="consent_updated",
            target_resource="ConsentRecord",
            details={"consent_type": data.consent_type, "status": data.status}
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(consent)
        return consent

    @staticmethod
    async def get_audit_logs(workspace_id: uuid.UUID, db: AsyncSession) -> List[GovernanceAuditLog]:
        query = select(GovernanceAuditLog).where(GovernanceAuditLog.workspace_id == workspace_id).order_by(GovernanceAuditLog.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def export_workspace_data(workspace_id: uuid.UUID, db: AsyncSession) -> dict:
        from app.models.workspace import Workspace
        # Fetch workspace details and policies
        result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
        workspace = result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Fetch Audit Logs
        logs = await GovernanceService.get_audit_logs(workspace_id, db)
        
        # Fetch DSRs
        dsrs = await GovernanceService.get_dsrs(workspace_id, None, db)

        return {
            "workspace": {
                "id": str(workspace.id),
                "name": workspace.name,
                "settings": workspace.settings
            },
            "audit_logs": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "actor_id": str(log.actor_id) if log.actor_id else None,
                    "details": log.details,
                    "created_at": log.created_at.isoformat()
                } for log in logs
            ],
            "dsrs": [
                {
                    "id": str(dsr.id),
                    "type": dsr.request_type.value,
                    "status": dsr.status.value,
                    "created_at": dsr.created_at.isoformat()
                } for dsr in dsrs
            ]
        }

    @staticmethod
    async def log_incident(workspace_id: uuid.UUID, reporter_id: uuid.UUID, data: dict, db: AsyncSession):
        from app.models.governance import SecurityIncident
        incident = SecurityIncident(
            workspace_id=workspace_id,
            reporter_id=reporter_id,
            title=data.title,
            description=data.description,
            severity=data.severity,
            status="open"
        )
        db.add(incident)
        
        audit_log = GovernanceAuditLog(
            workspace_id=workspace_id,
            actor_id=reporter_id,
            action="incident_logged",
            target_resource="SecurityIncident",
            details={"title": data.title, "severity": data.severity.value}
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(incident)
        return incident

    @staticmethod
    async def get_incidents(workspace_id: uuid.UUID, db: AsyncSession):
        from app.models.governance import SecurityIncident
        query = select(SecurityIncident).where(SecurityIncident.workspace_id == workspace_id).order_by(SecurityIncident.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
