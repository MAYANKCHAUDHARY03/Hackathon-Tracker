from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.database import get_db
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioResponse, PortfolioProjectAdd
)
from app.services.cross_portfolio_service import CrossPortfolioService

router = APIRouter(prefix="/workspaces/{workspace_id}/portfolios", tags=["Portfolios"])

@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    workspace_id: uuid.UUID,
    portfolio_in: PortfolioCreate,
    owner_type: str = "user",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(verify_workspace_access)
):
    """Create a new portfolio."""
    return await CrossPortfolioService.create_portfolio(db, workspace_id, current_user.id, owner_type, portfolio_in)

@router.get("", response_model=List[PortfolioResponse])
async def list_portfolios(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(verify_workspace_access)
):
    """List portfolios for the current user."""
    return await CrossPortfolioService.get_portfolios_for_owner(db, current_user.id)

@router.post("/{portfolio_id}/projects", response_model=PortfolioResponse)
async def add_project_to_portfolio(
    workspace_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    project_in: PortfolioProjectAdd,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(verify_workspace_access)
):
    """Add a project to a portfolio."""
    portfolio = await CrossPortfolioService.get_portfolio(db, portfolio_id)
    if not portfolio or portfolio.workspace_id != workspace_id or portfolio.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found or unauthorized")
        
    updated = await CrossPortfolioService.add_project_to_portfolio(db, portfolio_id, project_in.project_id)
    if not updated:
        raise HTTPException(status_code=400, detail="Project not found")
    return updated
