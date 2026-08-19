from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.portable_project import (
    PortableProjectIdentityCreate,
    PortableProjectIdentityResponse,
    ProjectStageTransitionCreate,
    ProjectStageTransitionResponse,
    PortableProjectHistoryResponse
)
from app.services.portable_project_service import PortableProjectService

router = APIRouter(prefix="/portable-projects", tags=["Portable Projects"])

@router.post("", response_model=PortableProjectIdentityResponse, status_code=status.HTTP_201_CREATED)
async def create_portable_project(
    data: PortableProjectIdentityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PortableProjectService(db)
    return await service.create_portable_project(current_user.id, data)

@router.get("/{project_id}", response_model=PortableProjectIdentityResponse)
async def get_portable_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PortableProjectService(db)
    return await service.get_portable_project(project_id, current_user.id)

@router.get("/{project_id}/history", response_model=PortableProjectHistoryResponse)
async def get_portable_project_history(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PortableProjectService(db)
    project, transitions = await service.get_project_history(project_id, current_user.id)
    return PortableProjectHistoryResponse(project=project, transitions=transitions)

@router.post("/{project_id}/transitions", response_model=ProjectStageTransitionResponse, status_code=status.HTTP_201_CREATED)
async def record_project_transition(
    project_id: UUID,
    data: ProjectStageTransitionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PortableProjectService(db)
    return await service.record_stage_transition(project_id, current_user.id, data)
