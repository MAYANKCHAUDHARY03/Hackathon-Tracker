from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.api_security import get_api_key, require_scopes
from app.models.api_auth import APIKey
from app.models.hackathon import Hackathon
from app.schemas.hackathon import HackathonResponse

router = APIRouter(prefix="/v1/hackathons", tags=["Public API - Hackathons"])

@router.get("", response_model=list[HackathonResponse])
async def list_hackathons(
    api_key: APIKey = Depends(require_scopes(["hackathons:read"])),
    db: AsyncSession = Depends(get_db)
):
    """
    List all hackathons in the workspace associated with the API key.
    Requires scope: 'hackathons:read'
    """
    stmt = select(Hackathon).where(Hackathon.workspace_id == api_key.workspace_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
