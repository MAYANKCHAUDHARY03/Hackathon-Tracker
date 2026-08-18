from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.portable_identity import (
    PortableIdentityUpdate, PortableIdentityResponse
)
from app.services.portable_identity_service import PortableIdentityService

router = APIRouter(
    prefix="/users/me/portable-identity",
    tags=["portable_identity"]
)

@router.get("", response_model=PortableIdentityResponse)
async def get_my_portable_identity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's portable identity settings."""
    return await PortableIdentityService.get_or_create_identity(current_user.id, db)

@router.patch("", response_model=PortableIdentityResponse)
async def update_my_portable_identity(
    data: PortableIdentityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update visibility and sharing settings for portable identity."""
    try:
        return await PortableIdentityService.update_identity(current_user.id, data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
