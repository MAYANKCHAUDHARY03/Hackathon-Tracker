from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.export_import import WorkspaceExport, ImportPreviewResponse, ImportExecuteRequest
from app.services.export_import_service import ExportImportService

router = APIRouter()

@router.get(
    "/workspaces/{workspace_id}/export",
    response_model=WorkspaceExport,
    status_code=200
)
async def export_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = ExportImportService(db)
    return await service.export_workspace(workspace_id)


@router.post(
    "/workspaces/{workspace_id}/import/preview",
    response_model=ImportPreviewResponse,
    status_code=200
)
async def preview_import(
    workspace_id: UUID,
    data: WorkspaceExport,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = ExportImportService(db)
    return await service.preview_import(data)


@router.post(
    "/workspaces/{workspace_id}/import/execute",
    status_code=200
)
async def execute_import(
    workspace_id: UUID,
    request: ImportExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = ExportImportService(db)
    success = await service.execute_import(workspace_id, request)
    return {"success": success}
