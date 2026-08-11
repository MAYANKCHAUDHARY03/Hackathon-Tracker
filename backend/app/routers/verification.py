from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.dependencies import get_current_user, require_workspace_admin
from app.services.verification_service import VerificationService
from app.schemas.verification import VerificationCreate, VerificationResponse

router = APIRouter(prefix="/workspaces/{workspace_id}/verifications", tags=["Verification"])

@router.post("", response_model=VerificationResponse, status_code=201)
async def request_verification(
    workspace_id: uuid.UUID,
    data: VerificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Request a new verification for an achievement or entity.
    """
    return await VerificationService.request_verification(db, workspace_id, data)

@router.post("/{verification_id}/verify", response_model=VerificationResponse)
async def verify_achievement(
    workspace_id: uuid.UUID,
    verification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_workspace_admin)
):
    """
    Verify an achievement. Only human/organizational admins can verify.
    """
    return await VerificationService.verify_achievement(
        db=db,
        verification_id=verification_id,
        verifier_id=current_user.id
    )

@router.post("/{verification_id}/reject", response_model=VerificationResponse)
async def reject_achievement(
    workspace_id: uuid.UUID,
    verification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_workspace_admin)
):
    """
    Reject a verification request.
    """
    return await VerificationService.reject_achievement(
        db=db,
        verification_id=verification_id,
        verifier_id=current_user.id
    )
