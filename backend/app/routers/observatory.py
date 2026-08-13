from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, get_db_ro
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access
from app.schemas.observatory import ObservatoryStats
from app.services.observatory_service import ObservatoryService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/observatory",
    tags=["observatory"]
)

@router.get("/stats", response_model=ObservatoryStats)
async def get_workspace_stats(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db_ro),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    Get aggregated high-level statistics for the workspace.
    Guarantees tenant isolation by only returning data strictly bounded to the workspace_id.
    """
    return await ObservatoryService.get_workspace_stats(workspace_id, db)
