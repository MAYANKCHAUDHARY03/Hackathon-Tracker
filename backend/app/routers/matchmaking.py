from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.database import get_db
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.matchmaking import (
    MatchProfileCreate, MatchProfileResponse,
    MatchOpportunityCreate, MatchOpportunityResponse,
    MatchRecommendationResponse
)
from app.services.matchmaking_service import MatchmakingService

router = APIRouter(prefix="/workspaces/{workspace_id}/matchmaking", tags=["Matchmaking"])

@router.post("/profiles", response_model=MatchProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    workspace_id: uuid.UUID,
    profile_in: MatchProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(verify_workspace_access)
):
    """Create a matchmaking profile for an entity."""
    return await MatchmakingService.create_profile(db, workspace_id, profile_in)

@router.post("/opportunities", response_model=MatchOpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    workspace_id: uuid.UUID,
    opportunity_in: MatchOpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_workspace_admin)
):
    """Create a new matchmaking opportunity (investor, mentor, grant)."""
    return await MatchmakingService.create_opportunity(
        db, workspace_id, provider_id=current_user.id, opp_in=opportunity_in
    )

@router.get("/opportunities", response_model=List[MatchOpportunityResponse])
async def list_opportunities(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(verify_workspace_access)
):
    """List opportunities in the workspace."""
    return await MatchmakingService.get_opportunities(db, workspace_id)

@router.post("/profiles/{profile_id}/recommendations", response_model=List[MatchRecommendationResponse])
async def generate_recommendations(
    workspace_id: uuid.UUID,
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(verify_workspace_access)
):
    """Generate recommendations for a profile."""
    profile = await MatchmakingService.get_profile(db, profile_id)
    if not profile or profile.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    return await MatchmakingService.generate_recommendations(db, profile_id)
