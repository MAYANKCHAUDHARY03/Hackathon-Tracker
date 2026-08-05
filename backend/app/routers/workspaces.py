from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, WorkspaceMembership
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=list[WorkspaceResponse])
async def get_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Workspace)
        .join(WorkspaceMembership)
        .where(WorkspaceMembership.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
