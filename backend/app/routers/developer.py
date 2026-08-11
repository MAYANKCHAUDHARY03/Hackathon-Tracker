from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.developer import (
    DeveloperAppCreate, DeveloperAppResponse,
    WebhookEndpointCreate, WebhookEndpointResponse
)
from app.services.developer_service import DeveloperService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/developer",
    tags=["developer"]
)

@router.post("/apps", response_model=DeveloperAppResponse)
async def create_developer_app(
    workspace_id: UUID,
    data: DeveloperAppCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Register a new OAuth/Developer app for this workspace."""
    return await DeveloperService.create_developer_app(workspace_id, data, db)

@router.get("/apps", response_model=List[DeveloperAppResponse])
async def get_developer_apps(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """List all Developer apps in this workspace."""
    return await DeveloperService.get_developer_apps(workspace_id, db)

@router.post("/webhooks", response_model=WebhookEndpointResponse)
async def create_webhook_endpoint(
    workspace_id: UUID,
    data: WebhookEndpointCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Register a new webhook endpoint."""
    return await DeveloperService.create_webhook_endpoint(workspace_id, data, db)

@router.get("/webhooks", response_model=List[WebhookEndpointResponse])
async def get_webhook_endpoints(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """List all webhook endpoints in this workspace."""
    return await DeveloperService.get_webhook_endpoints(workspace_id, db)
