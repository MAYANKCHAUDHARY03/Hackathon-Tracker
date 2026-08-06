from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter()

@router.get(
    "/workspaces/{workspace_id}/search",
    response_model=SearchResponse,
    status_code=200
)
async def search_workspace(
    workspace_id: UUID,
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Ensure user has access to workspace
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    
    search_service = SearchService(db)
    return await search_service.search(workspace_id, q)
