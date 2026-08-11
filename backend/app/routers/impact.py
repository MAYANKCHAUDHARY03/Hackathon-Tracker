from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.impact import (
    CustomMetricCreate, CustomMetricResponse,
    ProjectImpactUpdate, ProjectImpactResponse
)
from app.services.impact_service import ImpactService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/impact",
    tags=["impact"]
)

@router.post("/metrics", response_model=CustomMetricResponse)
async def create_custom_metric(
    workspace_id: UUID,
    data: CustomMetricCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Create a new custom metric definition for the workspace."""
    return await ImpactService.create_custom_metric(workspace_id, data, db)

@router.get("/metrics", response_model=List[CustomMetricResponse])
async def list_custom_metrics(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """List all custom metrics defined in the workspace."""
    return await ImpactService.list_custom_metrics(workspace_id, db)

@router.put("/projects/{project_id}", response_model=ProjectImpactResponse)
async def update_project_impact(
    workspace_id: UUID,
    project_id: UUID,
    data: ProjectImpactUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """Update the impact tracking (funnel stage and metrics) for a project."""
    try:
        return await ImpactService.update_project_impact(workspace_id, project_id, data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
