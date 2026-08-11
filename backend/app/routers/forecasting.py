from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access
from app.schemas.forecast import ForecastResponse
from app.services.forecasting_service import ForecastingService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/forecasting",
    tags=["forecasting"]
)

@router.post("/projects/{project_id}", response_model=ForecastResponse)
async def generate_project_forecast(
    workspace_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    Generate an AI forecast for a project.
    Output is explicitly labeled as a prediction and does not auto-trigger actions.
    """
    try:
        return await ForecastingService.generate_project_forecast(
            workspace_id=workspace_id,
            project_id=project_id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
