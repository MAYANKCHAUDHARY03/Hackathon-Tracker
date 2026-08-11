from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.federation import (
    WorkspaceFederationCreate, WorkspaceFederationUpdate, WorkspaceFederationResponse
)
from app.services.federation_service import FederationService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/federation",
    tags=["federation"]
)

@router.post("", response_model=WorkspaceFederationResponse)
async def create_federation_link(
    workspace_id: UUID,
    data: WorkspaceFederationCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Propose a new federation link with another workspace."""
    try:
        return await FederationService.create_federation_link(workspace_id, data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[WorkspaceFederationResponse])
async def get_federation_links(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """List all federation links (proposed and accepted) for this workspace."""
    return await FederationService.get_federation_links(workspace_id, db)

@router.put("/{federation_id}", response_model=WorkspaceFederationResponse)
async def update_federation_link(
    workspace_id: UUID,
    federation_id: UUID,
    data: WorkspaceFederationUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Update a federation link (e.g. target workspace accepts or rejects)."""
    try:
        return await FederationService.update_federation_link(workspace_id, federation_id, data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
