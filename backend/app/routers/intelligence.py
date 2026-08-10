from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.intelligence import EcosystemAnalyticsResponse
from app.services.intelligence_service import IntelligenceService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/ecosystem", response_model=EcosystemAnalyticsResponse)
async def get_ecosystem_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated ecosystem analytics.
    Privacy is maintained as this endpoint returns strictly aggregated and anonymized data.
    """
    return await IntelligenceService.get_ecosystem_analytics(db)
