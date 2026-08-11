import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.portfolio import Portfolio, PortfolioProject
from app.models.project import Project
from app.schemas.portfolio import PortfolioCreate

class CrossPortfolioService:
    @staticmethod
    async def create_portfolio(db: AsyncSession, workspace_id: uuid.UUID, owner_id: uuid.UUID, owner_type: str, pf_in: PortfolioCreate) -> Portfolio:
        pf = Portfolio(
            workspace_id=workspace_id,
            owner_id=owner_id,
            owner_type=owner_type,
            title=pf_in.title,
            description=pf_in.description,
            is_public=pf_in.is_public
        )
        db.add(pf)
        await db.commit()
        await db.refresh(pf)
        return await CrossPortfolioService.get_portfolio(db, pf.id)

    @staticmethod
    async def get_portfolio(db: AsyncSession, portfolio_id: uuid.UUID) -> Optional[Portfolio]:
        stmt = select(Portfolio).where(Portfolio.id == portfolio_id).options(selectinload(Portfolio.projects))
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_portfolios_for_owner(db: AsyncSession, owner_id: uuid.UUID) -> List[Portfolio]:
        stmt = select(Portfolio).where(Portfolio.owner_id == owner_id).options(selectinload(Portfolio.projects))
        result = await db.execute(stmt)
        return list(result.scalars().unique().all())

    @staticmethod
    async def add_project_to_portfolio(db: AsyncSession, portfolio_id: uuid.UUID, project_id: uuid.UUID) -> Optional[Portfolio]:
        # Verify project exists
        proj_result = await db.execute(select(Project).where(Project.id == project_id))
        proj = proj_result.scalars().first()
        if not proj:
            return None

        # Add link (ignore if exists)
        existing = await db.execute(
            select(PortfolioProject).where(
                PortfolioProject.portfolio_id == portfolio_id,
                PortfolioProject.project_id == project_id
            )
        )
        if not existing.scalars().first():
            link = PortfolioProject(portfolio_id=portfolio_id, project_id=project_id)
            db.add(link)
            await db.commit()
            
        stmt = select(Portfolio).where(Portfolio.id == portfolio_id).options(selectinload(Portfolio.projects)).execution_options(populate_existing=True)
        result = await db.execute(stmt)
        return result.scalars().first()
