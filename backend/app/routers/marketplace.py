import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.marketplace import MarketplaceProjectsResponse, MarketplacePartnersResponse
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.get("/projects", response_model=MarketplaceProjectsResponse)
async def get_marketplace_projects(
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    projects = await MarketplaceService.get_projects_seeking_partners(db, workspace_id)
    return {"projects": projects}

@router.get("/partners", response_model=MarketplacePartnersResponse)
async def get_marketplace_partners(
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    partners = await MarketplaceService.get_partners_seeking_projects(db, workspace_id)
    return {"partners": partners}
