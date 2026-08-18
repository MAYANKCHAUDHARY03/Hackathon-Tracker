import uuid
import enum
from sqlalchemy import String, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity

class VerificationLevel(str, enum.Enum):
    UNVERIFIED = "Unverified"
    SELF_DECLARED = "Self-Declared"
    PLATFORM_VERIFIED = "Platform-Verified"
    ORGANIZATION_VERIFIED = "Organization-Verified"
    MULTI_SOURCE_VERIFIED = "Multi-Source Verified"

class TrustVerification(BaseEntity):
    __tablename__ = "trust_verifications"

    target_type: Mapped[str] = mapped_column(String, index=True) # e.g. "skill", "achievement"
    target_id: Mapped[uuid.UUID] = mapped_column(index=True)
    
    verifier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verifier_org_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    
    level: Mapped[VerificationLevel] = mapped_column(Enum(VerificationLevel), default=VerificationLevel.UNVERIFIED)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
