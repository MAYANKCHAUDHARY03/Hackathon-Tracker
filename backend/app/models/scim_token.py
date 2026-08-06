from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseEntity

class ScimToken(BaseEntity):
    __tablename__ = "scim_tokens"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(100), nullable=True)
    token_hash = Column(String(255), nullable=False)
    
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization")
