import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, verify_workspace_access
from app.models.user import User, WorkspaceMembership
from app.schemas.notification import NotificationPreferenceResponse, NotificationPreferenceUpdate
from app.services.notification_service import get_preferences, update_preference

router = APIRouter(
    prefix="/workspaces/{workspace_id}/notification-preferences",
    tags=["notification-preferences"]
)

@router.get("", response_model=List[NotificationPreferenceResponse])
async def list_preferences(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await get_preferences(db, workspace_id, current_user.id)

@router.put("/{category}", response_model=NotificationPreferenceResponse)
async def modify_preference(
    workspace_id: uuid.UUID,
    category: str,
    update_data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await update_preference(
        db,
        workspace_id,
        current_user.id,
        category,
        update_data.model_dump(exclude_unset=True)
    )
