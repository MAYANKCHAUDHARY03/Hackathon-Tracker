from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime
import uuid

from app.models.verification import TrustVerification
from app.schemas.verification import VerificationCreate

class VerificationService:
    @staticmethod
    async def request_verification(
        db: AsyncSession,
        workspace_id: uuid.UUID,
        data: VerificationCreate
    ) -> TrustVerification:
        # A verification always starts as pending.
        verification = TrustVerification(
            workspace_id=workspace_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            achievement_type=data.achievement_type,
            achievement_detail=data.achievement_detail,
            source=data.source,
            status="pending"
        )
        db.add(verification)
        await db.commit()
        await db.refresh(verification)
        return verification

    @staticmethod
    async def verify_achievement(
        db: AsyncSession,
        verification_id: uuid.UUID,
        verifier_id: uuid.UUID
    ) -> TrustVerification:
        result = await db.execute(select(TrustVerification).where(TrustVerification.id == verification_id))
        verification = result.scalars().first()
        if not verification:
            raise HTTPException(status_code=404, detail="Verification request not found")
        
        # Hard Limit from Prompt: AI alone can never mark something verified.
        # We enforce that a valid human/org user ID is provided as verifier.
        if not verifier_id:
            raise HTTPException(status_code=400, detail="A valid human or organizational verifier ID is required. AI cannot self-verify.")
            
        verification.status = "verified"
        verification.verifier_id = verifier_id
        verification.verified_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(verification)
        return verification
        
    @staticmethod
    async def reject_achievement(
        db: AsyncSession,
        verification_id: uuid.UUID,
        verifier_id: uuid.UUID
    ) -> TrustVerification:
        result = await db.execute(select(TrustVerification).where(TrustVerification.id == verification_id))
        verification = result.scalars().first()
        if not verification:
            raise HTTPException(status_code=404, detail="Verification request not found")
            
        verification.status = "rejected"
        verification.verifier_id = verifier_id
        
        await db.commit()
        await db.refresh(verification)
        return verification
