from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.trust_verification import (
    TrustVerificationCreate, TrustVerificationResponse
)
from app.services.trust_service import TrustService

router = APIRouter(
    prefix="/trust",
    tags=["trust_layer"]
)

@router.post("/verify", response_model=TrustVerificationResponse)
async def verify_claim(
    data: TrustVerificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a verification to a claim (e.g. a skill or achievement)."""
    if not data.verifier_id:
        data.verifier_id = current_user.id
        
    return await TrustService.add_verification(data, db)

@router.get("/{target_type}/{target_id}", response_model=List[TrustVerificationResponse])
async def get_verifications(
    target_type: str,
    target_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the full evidence trail for a specific claim."""
    return await TrustService.get_verifications(target_type, target_id, db)
