from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.financing import FundingOpportunityResponse, FundingOpportunityCreate, OpportunityMatchResponse
from app.services.financing_intelligence import FinancingIntelligenceService

router = APIRouter(
    prefix="/financing",
    tags=["financing"]
)

@router.post("/opportunities", response_model=FundingOpportunityResponse)
async def create_opportunity(
    data: FundingOpportunityCreate,
    db: AsyncSession = Depends(get_db)
):
    return await FinancingIntelligenceService.create_opportunity(data, db)

@router.get("/matches/me", response_model=list[OpportunityMatchResponse])
async def get_my_matches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await FinancingIntelligenceService.find_matches_for_user(current_user.id, db)
