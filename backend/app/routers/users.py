from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.models.user import User
from app.models.governance import DataSubjectRequest, ConsentRecord
from app.schemas.user import UserResponse
from app.dependencies import get_current_user
from app.database import get_db

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/export", response_model=Dict[str, Any])
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all user data (Profile, Consents, DSRs)."""
    # Fetch user's DSRs
    dsr_result = await db.execute(select(DataSubjectRequest).where(DataSubjectRequest.user_id == current_user.id))
    dsrs = dsr_result.scalars().all()
    
    # Fetch user's Consents
    consent_result = await db.execute(select(ConsentRecord).where(ConsentRecord.user_id == current_user.id))
    consents = consent_result.scalars().all()

    return {
        "profile": {
            "id": str(current_user.id),
            "full_name": current_user.full_name,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        "dsrs": [
            {
                "id": str(d.id),
                "type": d.request_type.value,
                "status": d.status.value,
                "created_at": d.created_at.isoformat()
            } for d in dsrs
        ],
        "consents": [
            {
                "id": str(c.id),
                "type": c.consent_type,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            } for c in consents
        ]
    }

@router.delete("/me")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Anonymize user account to preserve graph integrity (RTBF)."""
    current_user.is_active = False
    current_user.full_name = "Deleted User"
    current_user.email = f"deleted_{current_user.id}@anonymized.local"
    current_user.avatar_url = None
    current_user.github_handle = None
    current_user.linkedin_url = None
    current_user.password_hash = "" # Remove password
    
    await db.commit()
    return {"message": "Account has been successfully deleted/anonymized"}
