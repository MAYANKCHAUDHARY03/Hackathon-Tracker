from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.governance import (
    DSRCreate, DSRResponse,
    ConsentCreate, ConsentResponse,
    AuditLogResponse
)
from app.services.governance_service import GovernanceService
from app.models.governance import DSRStatus

router = APIRouter(
    prefix="/workspaces/{workspace_id}/governance",
    tags=["governance"]
)

@router.post("/dsr", response_model=DSRResponse)
async def create_dsr(
    workspace_id: UUID,
    data: DSRCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """Create a Data Subject Request (GDPR/CCPA)."""
    return await GovernanceService.create_dsr(workspace_id, membership.user_id, data, db)

@router.get("/dsr", response_model=List[DSRResponse])
async def get_dsrs(
    workspace_id: UUID,
    user_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """List DSRs for a workspace (Admin only)."""
    return await GovernanceService.get_dsrs(workspace_id, user_id, db)

class DSRStatusUpdate(BaseModel):
    status: DSRStatus
    resolution_notes: str

@router.put("/dsr/{dsr_id}/status", response_model=DSRResponse)
async def update_dsr_status(
    workspace_id: UUID,
    dsr_id: UUID,
    data: DSRStatusUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Update DSR status (Admin only)."""
    return await GovernanceService.update_dsr_status(
        workspace_id, dsr_id, data.status, data.resolution_notes, membership.user_id, db
    )

@router.post("/consent", response_model=ConsentResponse)
async def record_consent(
    workspace_id: UUID,
    data: ConsentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """Record a user consent or revocation."""
    ip_address = request.client.host if request.client else "unknown"
    return await GovernanceService.record_consent(workspace_id, membership.user_id, data, ip_address, db)

@router.get("/audit", response_model=List[AuditLogResponse])
async def get_audit_logs(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Get audit logs for a workspace (Admin only)."""
    return await GovernanceService.get_audit_logs(workspace_id, db)
