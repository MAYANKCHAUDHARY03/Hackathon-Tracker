from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db, get_db_ro
from app.dependencies import get_current_user, verify_workspace_access
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.analytics import (
    WorkspaceAnalyticsSummary, 
    AnalyticsOverview, 
    AnalyticsDemographics, 
    AnalyticsEvaluations
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get(
    "/workspaces/{workspace_id}/analytics",
    response_model=WorkspaceAnalyticsSummary,
    status_code=200
)
async def get_workspace_analytics(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db_ro),
    current_user = Depends(get_current_user)
):
    # Ensure user has access to workspace
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_workspace_summary(workspace_id)


@router.get(
    "/workspaces/{workspace_id}/analytics/overview",
    response_model=AnalyticsOverview,
    status_code=200
)
async def get_overview(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db_ro),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_overview(workspace_id)


@router.get(
    "/workspaces/{workspace_id}/analytics/demographics",
    response_model=AnalyticsDemographics,
    status_code=200
)
async def get_demographics(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db_ro),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_demographics(workspace_id)


@router.get(
    "/workspaces/{workspace_id}/analytics/evaluations",
    response_model=AnalyticsEvaluations,
    status_code=200
)
async def get_evaluations(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db_ro),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_evaluations(workspace_id)


@router.get("/ecosystem/analytics", status_code=200)
async def get_ecosystem_analytics(db: AsyncSession = Depends(get_db_ro)):
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_ecosystem_summary()
