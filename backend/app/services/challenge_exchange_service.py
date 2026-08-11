import uuid
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.challenge import Challenge
from app.models.problem import Problem
from app.models.user import User

class ChallengeExchangeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_problem(self, workspace_id: uuid.UUID, problem_id: uuid.UUID) -> Optional[Problem]:
        stmt = select(Problem).where(
            Problem.workspace_id == workspace_id,
            Problem.id == problem_id
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def list_problems(
        self,
        workspace_id: uuid.UUID,
        domain: Optional[str] = None,
        status: Optional[str] = "open",
        limit: int = 50,
        offset: int = 0
    ) -> List[Problem]:
        conditions = [Problem.workspace_id == workspace_id]
        if domain:
            conditions.append(Problem.domain == domain)
        if status:
            conditions.append(Problem.status == status)

        stmt = select(Problem).where(and_(*conditions)).limit(limit).offset(offset)
        return list((await self.session.execute(stmt)).scalars().all())

    async def browse_challenges(
        self,
        workspace_id: uuid.UUID,
        category: Optional[str] = None,
        domain: Optional[str] = None,
        difficulty: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Challenge]:
        conditions = [
            Challenge.workspace_id == workspace_id,
            Challenge.visibility == "public",
            Challenge.status == "active"
        ]

        if category:
            conditions.append(Challenge.category == category)
        if domain:
            conditions.append(Challenge.domain == domain)
        if difficulty:
            conditions.append(Challenge.difficulty == difficulty)
        if search_term:
            term = f"%{search_term}%"
            conditions.append(
                or_(
                    Challenge.title.ilike(term),
                    Challenge.description.ilike(term)
                )
            )

        stmt = (
            select(Challenge)
            .options(selectinload(Challenge.problem))
            .where(and_(*conditions))
            .order_by(Challenge.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        return list((await self.session.execute(stmt)).scalars().all())

    async def express_interest(
        self,
        workspace_id: uuid.UUID,
        challenge_id: uuid.UUID,
        user_id: uuid.UUID
    ):
        """
        Record user interest in a challenge via the Knowledge Graph.
        """
        from app.models.graph import GraphEdge
        
        stmt = select(GraphEdge).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.source_id == user_id,
            GraphEdge.target_id == challenge_id,
            GraphEdge.relationship_type == "interested_in"
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        
        if not existing:
            edge = GraphEdge(
                workspace_id=workspace_id,
                source_id=user_id,
                source_type="user",
                target_id=challenge_id,
                target_type="challenge",
                relationship_type="interested_in",
                provenance="user-provided",
                confidence=1.0,
                created_by=user_id
            )
            self.session.add(edge)
            
            # Increment interest/submission count just as a loose metric
            chal_stmt = select(Challenge).where(Challenge.id == challenge_id)
            challenge = (await self.session.execute(chal_stmt)).scalars().first()
            if challenge:
                challenge.submission_count = (challenge.submission_count or 0) + 1
                
            await self.session.commit()
