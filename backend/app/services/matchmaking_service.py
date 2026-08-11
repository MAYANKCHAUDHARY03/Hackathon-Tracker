import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.matchmaking import MatchProfile, MatchOpportunity, MatchRecommendation
from app.schemas.matchmaking import MatchProfileCreate, MatchOpportunityCreate

class MatchmakingService:
    @staticmethod
    async def create_profile(db: AsyncSession, workspace_id: uuid.UUID, profile_in: MatchProfileCreate) -> MatchProfile:
        profile = MatchProfile(
            workspace_id=workspace_id,
            entity_type=profile_in.entity_type,
            entity_id=profile_in.entity_id,
            tags=profile_in.tags,
            needs=profile_in.needs
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    @staticmethod
    async def create_opportunity(db: AsyncSession, workspace_id: uuid.UUID, provider_id: uuid.UUID, opp_in: MatchOpportunityCreate) -> MatchOpportunity:
        opp = MatchOpportunity(
            workspace_id=workspace_id,
            title=opp_in.title,
            description=opp_in.description,
            opportunity_type=opp_in.opportunity_type,
            tags=opp_in.tags,
            provider_id=provider_id
        )
        db.add(opp)
        await db.commit()
        await db.refresh(opp)
        return opp

    @staticmethod
    async def get_profile(db: AsyncSession, profile_id: uuid.UUID) -> Optional[MatchProfile]:
        result = await db.execute(select(MatchProfile).where(MatchProfile.id == profile_id))
        return result.scalars().first()

    @staticmethod
    async def get_opportunities(db: AsyncSession, workspace_id: uuid.UUID) -> List[MatchOpportunity]:
        result = await db.execute(select(MatchOpportunity).where(MatchOpportunity.workspace_id == workspace_id))
        return list(result.scalars().all())

    @staticmethod
    async def generate_recommendations(db: AsyncSession, profile_id: uuid.UUID) -> List[MatchRecommendation]:
        # Basic heuristic: match by overlapping tags
        profile = await MatchmakingService.get_profile(db, profile_id)
        if not profile:
            return []
            
        opportunities = await MatchmakingService.get_opportunities(db, profile.workspace_id)
        
        recommendations = []
        profile_tags = set(tag.lower() for tag in profile.tags)
        
        for opp in opportunities:
            opp_tags = set(tag.lower() for tag in opp.tags)
            overlap = profile_tags.intersection(opp_tags)
            
            if overlap:
                # Basic score: 20 points per overlapping tag, max 100
                score = min(len(overlap) * 20, 100)
                
                # Check if recommendation already exists
                existing = await db.execute(
                    select(MatchRecommendation).where(
                        MatchRecommendation.profile_id == profile.id,
                        MatchRecommendation.opportunity_id == opp.id
                    )
                )
                rec = existing.scalars().first()
                if not rec:
                    rec = MatchRecommendation(
                        workspace_id=profile.workspace_id,
                        profile_id=profile.id,
                        opportunity_id=opp.id,
                        score=score,
                        status="suggested"
                    )
                    db.add(rec)
                    recommendations.append(rec)
                else:
                    # Update score if needed
                    if rec.score != score:
                        rec.score = score
                    recommendations.append(rec)
                    
        if recommendations:
            await db.commit()
            for rec in recommendations:
                await db.refresh(rec)
                
        # Re-fetch with relationships loaded
        stmt = select(MatchRecommendation).where(
            MatchRecommendation.profile_id == profile_id
        ).options(
            selectinload(MatchRecommendation.profile),
            selectinload(MatchRecommendation.opportunity)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
