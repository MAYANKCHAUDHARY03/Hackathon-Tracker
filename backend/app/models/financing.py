import uuid
from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity

class FundingOpportunity(BaseEntity):
    __tablename__ = "funding_opportunities"

    title: Mapped[str] = mapped_column(String, index=True)
    opportunity_type: Mapped[str] = mapped_column(String) # e.g. "Grant", "VC", "Accelerator", "Competition"
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")
    
    sponsor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    sponsor_name: Mapped[str] = mapped_column(String)
    
    # Requirements criteria: e.g. {"required_skills": ["Machine Learning"], "min_verification_level": "Platform-Verified"}
    criteria: Mapped[dict] = mapped_column(JSON, default=dict)
    
    description: Mapped[str] = mapped_column(String)
