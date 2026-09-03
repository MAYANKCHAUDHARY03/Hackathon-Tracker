import uuid
import enum
from sqlalchemy import String, ForeignKey, Enum, JSON, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing

from app.models.base import BaseEntity

if typing.TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization

class FederationStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"

class FederatedIdentity(BaseEntity):
    __tablename__ = "federated_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    home_org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    target_org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    
    status: Mapped[FederationStatus] = mapped_column(
        Enum(FederationStatus), default=FederationStatus.ACTIVE
    )
    
    # intersection of the user's home permissions and the OrganizationTrust allowed_scopes
    granted_scopes: Mapped[list] = mapped_column(JSON, default=list) 
    
    user: Mapped["User"] = relationship("User")
    home_org: Mapped["Organization"] = relationship("Organization", foreign_keys=[home_org_id])
    target_org: Mapped["Organization"] = relationship("Organization", foreign_keys=[target_org_id])

    __table_args__ = (
        Index("ix_fed_identity_link", "user_id", "home_org_id", "target_org_id", unique=True),
    )
