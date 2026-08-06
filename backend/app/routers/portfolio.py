from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.portfolio import UserPortfolio
from app.services.portfolio_service import PortfolioService

router = APIRouter()

@router.get(
    "/users/{user_id}/portfolio",
    response_model=UserPortfolio,
    status_code=200
)
async def get_user_portfolio(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = PortfolioService(db)
    try:
        return await service.get_user_portfolio(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
