import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.incubation_service import IncubationService
from app.schemas.incubation import (
    ProjectUpdateCreate,
    ProjectDocumentCreate,
    ProjectFundingCreate,
    IncubationDashboardResponse,
    ProjectUpdateResponse,
    ProjectDocumentResponse,
    ProjectFundingResponse
)
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["incubation"])

@router.get("/{project_id}/incubation/dashboard", response_model=IncubationDashboardResponse)
async def get_incubation_dashboard(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IncubationService(db)
    return await service.get_dashboard(project_id)

@router.post("/{project_id}/incubation/updates", response_model=ProjectUpdateResponse)
async def create_project_update(
    project_id: uuid.UUID,
    data: ProjectUpdateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IncubationService(db)
    return await service.create_update(project_id, data, current_user.id)

@router.post("/{project_id}/incubation/documents", response_model=ProjectDocumentResponse)
async def create_project_document(
    project_id: uuid.UUID,
    data: ProjectDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IncubationService(db)
    return await service.create_document(project_id, data, current_user.id)

@router.post("/{project_id}/incubation/funding", response_model=ProjectFundingResponse)
async def create_project_funding(
    project_id: uuid.UUID,
    data: ProjectFundingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IncubationService(db)
    return await service.create_funding_round(project_id, data)

@router.post("/{project_id}/incubation/stakeholders")
async def add_stakeholder(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This is a simplification. Usually we'd look up the workspace ID from the project.
    # We will hardcode workspace_id for now or fetch it from the project.
    from sqlalchemy import select
    from app.models.project import Project
    
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    service = IncubationService(db)
    await service.add_stakeholder(project.workspace_id, project_id, user_id, role)
    return {"status": "success"}
