from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.user import User
from app.models.team import Team, TeamMember
from app.schemas.portfolio import UserPortfolio, PortfolioItem

class PortfolioService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_portfolio(self, user_id: UUID) -> UserPortfolio:
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
            
        stmt = select(Team).join(TeamMember).where(TeamMember.user_id == user_id)
        teams = (await self.session.execute(stmt)).scalars().all()
        
        items = []
        for team in teams:
            items.append(PortfolioItem(
                id=str(team.id),
                name=team.name,
                description=team.description,
                type="team",
                url=None,
                date=team.created_at
            ))
            
        return UserPortfolio(
            user_id=str(user.id),
            full_name=user.full_name,
            bio=None,
            items=items
        )
