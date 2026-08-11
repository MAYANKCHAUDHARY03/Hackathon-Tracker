from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access
from app.schemas.network import NetworkResolveRequest, NetworkResolveResponse
from app.services.network_service import NetworkService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/network",
    tags=["network"]
)

@router.post("/resolve", response_model=NetworkResolveResponse)
async def resolve_network(
    workspace_id: UUID,
    request: NetworkResolveRequest,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    Resolve the Innovation Network topology around a query.
    Shows the lifecycle: Problem -> Challenge -> Project -> Impact.
    """
    return await NetworkService.resolve_network(workspace_id, request, db)
