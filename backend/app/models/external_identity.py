from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseEntity

class ExternalIdentity(BaseEntity):
    __tablename__ = "external_identities"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(String(36), ForeignKey("identity_providers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    external_subject = Column(String(255), nullable=False)
    external_email = Column(String(255), nullable=True)
    
    last_authenticated_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("provider_id", "external_subject", name="uq_provider_subject"),
    )

    # Relationships
    organization = relationship("Organization")
    user = relationship("User", backref="external_identities")
    provider = relationship("IdentityProvider", backref="external_identities")
