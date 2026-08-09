from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.services.matching_service import EcosystemMatchingEngine
from pydantic import BaseModel

router = APIRouter()

class MatchScoreRequest(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID

class MatchScoreResponse(BaseModel):
    score: float

class MatchFindRequest(BaseModel):
    source_id: uuid.UUID
    target_type: str
    limit: int = 10

class MatchResult(BaseModel):
    node_id: str
    type: str
    score: float
    data: dict

@router.post("/workspaces/{workspace_id}/matching/score", response_model=MatchScoreResponse)
async def compute_match_score(
    workspace_id: uuid.UUID,
    req: MatchScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = EcosystemMatchingEngine(db)
    score = await engine.compute_match_score(workspace_id, req.source_id, req.target_id)
    return MatchScoreResponse(score=score)

@router.post("/workspaces/{workspace_id}/matching/find", response_model=List[MatchResult])
async def find_matches(
    workspace_id: uuid.UUID,
    req: MatchFindRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = EcosystemMatchingEngine(db)
    matches = await engine.find_matches(workspace_id, req.source_id, req.target_type, req.limit)
    return matches
