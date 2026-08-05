from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/dashboard",
    tags=["dashboard"]
)

@router.get("", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    Get dashboard summary statistics and widgets data for a specific workspace.
    Accessible by any workspace member.
    """
    return await DashboardService.get_dashboard_summary(db=db, workspace_id=workspace_id)
