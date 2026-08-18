from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.trust_verification import TrustVerification, VerificationLevel
from app.models.portable_identity import VerifiedSkill
from app.schemas.trust_verification import TrustVerificationCreate, TrustVerificationResponse

class TrustService:
    @staticmethod
    async def add_verification(data: TrustVerificationCreate, db: AsyncSession) -> TrustVerificationResponse:
        verification = TrustVerification(**data.model_dump())
        db.add(verification)
        await db.commit()
        await db.refresh(verification)
        
        # If this is verifying a skill, try to upgrade the skill's trust level
        if data.target_type == "skill":
            skill_query = select(VerifiedSkill).where(VerifiedSkill.id == data.target_id)
            res = await db.execute(skill_query)
            skill = res.scalar_one_or_none()
            if skill:
                # Upgrading logic based on level weights
                levels = list(VerificationLevel)
                current_idx = levels.index(VerificationLevel(skill.verification_level))
                new_idx = levels.index(data.level)
                
                if new_idx > current_idx:
                    skill.verification_level = data.level.value
                    
                # Append evidence
                current_evidence = list(skill.evidence_trail) if skill.evidence_trail else []
                current_evidence.append(data.evidence)
                skill.evidence_trail = current_evidence
                
                await db.commit()
                
        return TrustVerificationResponse.model_validate(verification)

    @staticmethod
    async def get_verifications(target_type: str, target_id: UUID, db: AsyncSession):
        query = select(TrustVerification).where(
            TrustVerification.target_type == target_type,
            TrustVerification.target_id == target_id
        )
        result = await db.execute(query)
        verifications = result.scalars().all()
        return [TrustVerificationResponse.model_validate(v) for v in verifications]
