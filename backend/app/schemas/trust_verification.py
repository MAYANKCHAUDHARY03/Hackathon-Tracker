from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.trust_verification import VerificationLevel

class TrustVerificationBase(BaseModel):
    target_type: str
    target_id: UUID
    verifier_id: UUID | None = None
    verifier_org_id: UUID | None = None
    level: VerificationLevel = VerificationLevel.UNVERIFIED
    evidence: dict = {}

class TrustVerificationCreate(TrustVerificationBase):
    pass

class TrustVerificationResponse(TrustVerificationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
