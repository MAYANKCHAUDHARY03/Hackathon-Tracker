import uuid
import enum
from sqlalchemy import String, ForeignKey, Enum, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing

from app.models.base import BaseEntity

if typing.TYPE_CHECKING:
    from app.models.organization import Organization

class TrustStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    REVOKED = "revoked"

class OrganizationTrust(BaseEntity):
    __tablename__ = "organization_trusts"

    trustor_org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    trustee_org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    
    status: Mapped[TrustStatus] = mapped_column(
        Enum(TrustStatus), default=TrustStatus.PENDING
    )
    
    # Scopes limit what roles/access the federated users from the trustee org can assume in the trustor org
    allowed_scopes: Mapped[list] = mapped_column(JSON, default=list) # e.g. ["federated_reviewer", "federated_participant"]
    
    trustor: Mapped["Organization"] = relationship("Organization", foreign_keys=[trustor_org_id])
    trustee: Mapped["Organization"] = relationship("Organization", foreign_keys=[trustee_org_id])

    __table_args__ = (
        Index("ix_org_trust_link", "trustor_org_id", "trustee_org_id", unique=True),
    )
