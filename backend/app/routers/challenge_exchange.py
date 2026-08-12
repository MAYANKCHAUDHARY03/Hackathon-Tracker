import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.schemas.challenge_exchange import ProblemListResponse, ChallengeListResponse
from app.services.challenge_exchange_service import ChallengeExchangeService

router = APIRouter(prefix="/challenge-exchange", tags=["challenge-exchange"])

@router.get("/problems", response_model=ProblemListResponse)
async def list_problems(
    workspace_id: uuid.UUID = Query(...),
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query("open"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = ChallengeExchangeService(db)
    problems = await service.list_problems(
        workspace_id=workspace_id, 
        domain=domain, 
        status=status, 
        limit=limit, 
        offset=offset
    )
    return {"problems": problems}

@router.get("/challenges", response_model=ChallengeListResponse)
async def browse_challenges(
    workspace_id: uuid.UUID = Query(...),
    category: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search_term: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = ChallengeExchangeService(db)
    challenges = await service.browse_challenges(
        workspace_id=workspace_id,
        category=category,
        domain=domain,
        difficulty=difficulty,
        search_term=search_term,
        limit=limit,
        offset=offset
    )
    return {"challenges": challenges}

@router.post("/challenges/{challenge_id}/interest")
async def express_interest(
    challenge_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = ChallengeExchangeService(db)
    await service.express_interest(
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        user_id=current_user.id
    )
    return {"status": "success"}
