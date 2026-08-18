from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.financing import FundingOpportunity
from app.models.portable_identity import PortableIdentity, VerifiedSkill
from app.schemas.financing import FundingOpportunityCreate, FundingOpportunityResponse, OpportunityMatchResponse

class FinancingIntelligenceService:
    @staticmethod
    async def create_opportunity(data: FundingOpportunityCreate, db: AsyncSession) -> FundingOpportunityResponse:
        opp = FundingOpportunity(**data.model_dump())
        db.add(opp)
        await db.commit()
        await db.refresh(opp)
        return FundingOpportunityResponse.model_validate(opp)

    @staticmethod
    async def find_matches_for_user(user_id: UUID, db: AsyncSession) -> list[OpportunityMatchResponse]:
        # 1. Fetch user's identity and verified skills
        identity_query = select(PortableIdentity).where(PortableIdentity.user_id == user_id)
        res = await db.execute(identity_query)
        identity = res.scalar_one_or_none()
        
        if not identity:
            return []
            
        skills_query = select(VerifiedSkill).where(VerifiedSkill.identity_id == identity.id)
        res = await db.execute(skills_query)
        skills = res.scalars().all()
        skill_names = [s.skill_name.lower() for s in skills]
        
        # 2. Fetch all opportunities
        opps_query = select(FundingOpportunity)
        res = await db.execute(opps_query)
        opportunities = res.scalars().all()
        
        # 3. Match logic
        matches = []
        for opp in opportunities:
            required_skills = opp.criteria.get("required_skills", [])
            matched_criteria = []
            missing_criteria = []
            
            for req in required_skills:
                if req.lower() in skill_names:
                    matched_criteria.append(req)
                else:
                    missing_criteria.append(req)
                    
            if not required_skills:
                score = 0.5 # baseline
            else:
                score = len(matched_criteria) / len(required_skills)
                
            if score >= 0.5: # only return good matches
                matches.append(OpportunityMatchResponse(
                    opportunity=FundingOpportunityResponse.model_validate(opp),
                    match_score=score,
                    matched_criteria=matched_criteria,
                    missing_criteria=missing_criteria
                ))
                
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches
