from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.models.user import User, WorkspaceMembership
from app.dependencies import get_current_user, verify_workspace_access, require_workspace_admin
from app.schemas.hackathon import (
    HackathonCreate,
    HackathonUpdate,
    HackathonResponse,
    HackathonListResponse
)
from app.services.hackathon_service import HackathonService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/hackathons",
    tags=["hackathons"]
)

@router.post("", response_model=HackathonResponse, status_code=status.HTTP_201_CREATED)
async def create_hackathon(
    workspace_id: UUID,
    hackathon_in: HackathonCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new hackathon. Requires owner or admin role.
    """
    return await HackathonService.create_hackathon(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id,
        hackathon_data=hackathon_in
    )

@router.get("", response_model=HackathonListResponse)
async def list_hackathons(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    mode: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    include_archived: bool = Query(False),
    is_template: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    List hackathons for a workspace. Accessible by any workspace member.
    """
    items, total = await HackathonService.get_hackathons(
        db=db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        search=search,
        mode=mode,
        status_filter=status_filter,
        include_archived=include_archived,
        is_template=is_template
    )
    return HackathonListResponse(items=items, total=total)

@router.get("/templates", response_model=HackathonListResponse)
async def list_templates(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    List all available program templates.
    """
    items, total = await HackathonService.get_hackathons(
        db=db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        is_template=True
    )
    return HackathonListResponse(items=items, total=total)

@router.get("/{hackathon_id}", response_model=HackathonResponse)
async def get_hackathon(
    workspace_id: UUID,
    hackathon_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    Get a specific hackathon by ID.
    """
    return await HackathonService.get_hackathon_by_id(db, workspace_id, hackathon_id)

@router.post("/from-template/{template_id}", response_model=HackathonResponse, status_code=status.HTTP_201_CREATED)
async def create_from_template(
    workspace_id: UUID,
    template_id: UUID,
    hackathon_in: HackathonCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new program from a template. Requires owner or admin role.
    """
    return await HackathonService.create_from_template(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id,
        template_id=template_id,
        hackathon_data=hackathon_in
    )

@router.put("/{hackathon_id}", response_model=HackathonResponse)
async def update_hackathon(
    workspace_id: UUID,
    hackathon_id: UUID,
    hackathon_in: HackathonUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """
    Update a hackathon. Requires owner or admin role.
    """
    return await HackathonService.update_hackathon(db, workspace_id, hackathon_id, hackathon_in)

@router.post("/{hackathon_id}/archive", response_model=HackathonResponse)
async def archive_hackathon(
    workspace_id: UUID,
    hackathon_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """
    Archive a hackathon. Requires owner or admin role.
    """
    return await HackathonService.archive_hackathon(db, workspace_id, hackathon_id)

@router.post("/{hackathon_id}/restore", response_model=HackathonResponse)
async def restore_hackathon(
    workspace_id: UUID,
    hackathon_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """
    Restore an archived hackathon. Requires owner or admin role.
    """
    return await HackathonService.restore_hackathon(db, workspace_id, hackathon_id)

@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hackathon(
    workspace_id: UUID,
    hackathon_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """
    Permanently delete a hackathon. Requires owner or admin role.
    """
    await HackathonService.delete_hackathon(db, workspace_id, hackathon_id)
