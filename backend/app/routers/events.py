import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.event import EventResponse
from app.services.event_service import EventService

router = APIRouter()

@router.get("", response_model=List[EventResponse])
async def get_events(
    workspace_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Depending on auth models, we would check if current_user belongs to workspace_id
    # Assuming basic check here, though actual app might have deeper integration
    service = EventService(db)
    events = await service.get_events(workspace_id=workspace_id, limit=limit, offset=offset)
    return events
