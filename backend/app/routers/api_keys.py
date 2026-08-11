import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_workspace_admin, verify_workspace_access
from app.models.user import User
from app.schemas.api_auth import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse
from app.services.api_auth_service import APIKeyService

router = APIRouter(prefix="/workspaces/{workspace_id}/api-keys", tags=["API Keys"])

@router.post("", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    workspace_id: uuid.UUID,
    data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_workspace_admin)
):
    """Generate a new API key for the workspace"""
    api_key_service = APIKeyService(db)
    api_key, raw_key = await api_key_service.create_api_key(
        workspace_id=workspace_id,
        user_id=current_user.id,
        data=data,
        prefix="ht_live_"  # E.g., 'ht_test_' could be used if we support test mode later
    )
    
    # We must construct a dictionary that mimics the APIKeyCreateResponse model
    response_data = {
        "id": api_key.id,
        "name": api_key.name,
        "prefix": api_key.prefix,
        "scopes": api_key.scopes,
        "expires_at": api_key.expires_at,
        "last_used_at": api_key.last_used_at,
        "is_active": api_key.is_active,
        "created_at": api_key.created_at,
        "key": raw_key  # This is the only time the raw key is ever returned
    }
    
    return response_data

@router.get("", response_model=list[APIKeyResponse])
async def list_api_keys(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_workspace_access)
):
    """List all API keys for the workspace"""
    api_key_service = APIKeyService(db)
    return await api_key_service.get_workspace_api_keys(workspace_id)

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    workspace_id: uuid.UUID,
    key_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_workspace_admin)
):
    """Revoke (deactivate) an API key"""
    api_key_service = APIKeyService(db)
    await api_key_service.revoke_api_key(key_id=key_id, workspace_id=workspace_id)
