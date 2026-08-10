import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.calendar import CalendarEvent
from app.services.workspace_calendar_service import WorkspaceCalendarService

router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/calendar",
    response_model=List[CalendarEvent],
    status_code=200,
)
async def get_workspace_calendar(
    workspace_id: uuid.UUID,
    start: datetime = Query(..., description="Start of date range (ISO 8601)"),
    end: datetime = Query(..., description="End of date range (ISO 8601)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _membership=Depends(verify_workspace_access),
):
    """
    Returns all calendar events across the workspace for the given date range.
    Aggregates hackathon dates, round schedules, and deadlines.
    """
    service = WorkspaceCalendarService(db)
    return await service.get_workspace_events(workspace_id, start, end)
