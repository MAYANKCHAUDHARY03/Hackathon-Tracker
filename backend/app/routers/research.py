from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.models.user import User
from app.schemas.research import ResearchLinkCreate, ResearchLinkUpdate, ResearchLinkResponse
from app.services.research_service import ResearchService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/research",
    tags=["research"],
    dependencies=[Depends(verify_workspace_access)]
)

@router.post("/", response_model=ResearchLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_research_link(
    workspace_id: uuid.UUID,
    data: ResearchLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ResearchService.create_link(db, workspace_id, current_user.id, data)

@router.get("/project/{project_id}", response_model=List[ResearchLinkResponse])
async def get_project_research_links(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    return await ResearchService.get_links_for_project(db, workspace_id, project_id)

@router.put("/{link_id}", response_model=ResearchLinkResponse)
async def update_research_link(
    workspace_id: uuid.UUID,
    link_id: uuid.UUID,
    data: ResearchLinkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ResearchService.update_link(db, workspace_id, link_id, current_user.id, data)

@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_link(
    workspace_id: uuid.UUID,
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    await ResearchService.delete_link(db, workspace_id, link_id)
