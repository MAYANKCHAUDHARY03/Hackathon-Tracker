from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.audit import AuditLogListResponse
from app.services.audit_service import AuditService

router = APIRouter()

@router.get(
    "/workspaces/{workspace_id}/audit-logs",
    response_model=AuditLogListResponse,
    status_code=200
)
async def get_audit_logs(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Ensure user has access to workspace
    # Additional check could ensure only 'admin' or 'auditor' can access this.
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    
    audit_service = AuditService(db)
    logs, total = await audit_service.get_logs(workspace_id, skip, limit)
    
    return AuditLogListResponse(items=logs, total=total)
