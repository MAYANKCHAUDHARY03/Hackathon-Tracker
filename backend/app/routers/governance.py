from uuid import UUID
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.governance import (
    DSRCreate, DSRResponse,
    ConsentCreate, ConsentResponse,
    AuditLogResponse, WorkspacePolicy, WorkspacePolicyUpdate
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

@router.get("/policy", response_model=WorkspacePolicy)
async def get_policy(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Get governance policies for a workspace."""
    # Policies are stored in workspace.settings
    from app.models.workspace import Workspace
    from sqlalchemy import select
    from fastapi import HTTPException

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Return default policy if not set
    policy_data = workspace.settings.get("governance_policy", {})
    return WorkspacePolicy(**policy_data)

@router.put("/policy", response_model=WorkspacePolicy)
async def update_policy(
    workspace_id: UUID,
    data: WorkspacePolicyUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Update governance policies for a workspace."""
    from app.models.workspace import Workspace
    from sqlalchemy import select
    from fastapi import HTTPException
    import copy

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    settings = copy.deepcopy(workspace.settings)
    settings["governance_policy"] = data.model_dump()
    workspace.settings = settings
    await db.commit()

    # Log policy change
    from app.models.governance import GovernanceAuditLog
    audit_log = GovernanceAuditLog(
        workspace_id=workspace_id,
        actor_id=membership.user_id,
        action="UPDATE_WORKSPACE_POLICY",
        target_resource="WORKSPACE_SETTINGS",
        target_id=str(workspace_id),
        details={"new_policy": data.model_dump()}
    )
    db.add(audit_log)
    await db.commit()

    return data

@router.get("/export", response_model=Dict[str, Any])
async def export_workspace_data(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Export all governance data for a workspace (Admin only)."""
    return await GovernanceService.export_workspace_data(workspace_id, db)

from app.schemas.governance import SecurityIncidentCreate, SecurityIncidentResponse

@router.post("/incidents", response_model=SecurityIncidentResponse)
async def log_incident(
    workspace_id: UUID,
    data: SecurityIncidentCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Log a security or privacy incident (Admin only)."""
    return await GovernanceService.log_incident(workspace_id, membership.user_id, data, db)

@router.get("/incidents", response_model=List[SecurityIncidentResponse])
async def get_incidents(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """View logged incidents (All workspace members)."""
    return await GovernanceService.get_incidents(workspace_id, db)
