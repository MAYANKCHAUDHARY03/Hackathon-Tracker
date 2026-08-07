import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, verify_workspace_access
from app.models.user import User, WorkspaceMembership
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationSummaryResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationPreferenceCreate
)
from app.services.notification_service import (
    get_notifications,
    get_unread_count,
    get_notification_summary,
    mark_read,
    mark_all_read,
    dismiss
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/notifications",
    tags=["notifications"]
)

@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    workspace_id: uuid.UUID,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    is_read: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    items, total, unread_count = await get_notifications(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id,
        category=category,
        severity=severity,
        is_read=is_read,
        skip=skip,
        limit=limit
    )
    return NotificationListResponse(items=items, total=total, unread_count=unread_count)

@router.get("/unread/count")
async def get_unread(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    count = await get_unread_count(db, workspace_id, current_user.id)
    return {"count": count}

@router.get("/summary", response_model=NotificationSummaryResponse)
async def get_summary(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await get_notification_summary(db, workspace_id, current_user.id)

@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    workspace_id: uuid.UUID,
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await mark_read(db, workspace_id, current_user.id, notification_id)

@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_notifications_read(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    await mark_all_read(db, workspace_id, current_user.id)

@router.post("/{notification_id}/dismiss", response_model=NotificationResponse)
async def dismiss_notification(
    workspace_id: uuid.UUID,
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await dismiss(db, workspace_id, current_user.id, notification_id)

from app.services.reminder_service import run_reminder_engine

@router.post("/_internal/generate-reminders", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reminders(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    # In a real app this might be a background task or run globally.
    # We trigger it per workspace for testing.
    await run_reminder_engine(db, workspace_id)
    return {"status": "accepted"}
