from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseEntity

class IdentityProvider(BaseEntity):
    __tablename__ = "identity_providers"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_type = Column(String(50), nullable=False) # 'oidc' or 'saml'
    display_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="draft") # draft, active, suspended, archived
    
    # Provider config
    issuer = Column(String(255), nullable=True)
    client_id = Column(String(255), nullable=True)
    encrypted_client_secret = Column(Text, nullable=True)
    discovery_url = Column(String(255), nullable=True)
    metadata_url = Column(String(255), nullable=True)
    certificate_reference = Column(Text, nullable=True)
    
    # JSON list of allowed domains
    allowed_domains = Column(JSON, nullable=True)
    
    # Provisioning behavior
    auto_provision_users = Column(Boolean, default=False)
    auto_link_existing_users = Column(Boolean, default=False)
    default_role = Column(String(50), default="member")
    
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    archived_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", backref="identity_providers")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
