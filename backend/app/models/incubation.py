from enum import Enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseEntity

class ProjectUpdateType(str, Enum):
    PROGRESS_REPORT = "progress_report"
    INVESTOR_UPDATE = "investor_update"
    KPI = "kpi"

class ProjectDocumentType(str, Enum):
    BUSINESS_PLAN = "business_plan"
    PITCH_DECK = "pitch_deck"
    LEGAL = "legal"
    FINANCIAL = "financial"
    OTHER = "other"

class ProjectFundingRoundType(str, Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GRANT = "grant"
    ANGEL = "angel"
    OTHER = "other"

class ProjectUpdate(BaseEntity):
    __tablename__ = "project_updates"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    update_type: Mapped[str] = mapped_column(String, nullable=False, default=ProjectUpdateType.PROGRESS_REPORT.value)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # JSON field for KPIs (e.g. {"mrr": 5000, "users": 1200})
    kpi_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    project = relationship("Project", backref="updates")
    author = relationship("User")


class ProjectDocument(BaseEntity):
    __tablename__ = "project_documents"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    uploaded_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[str] = mapped_column(String, nullable=False, default=ProjectDocumentType.OTHER.value)
    url: Mapped[str] = mapped_column(String, nullable=False)
    
    project = relationship("Project", backref="documents")
    uploaded_by = relationship("User")


class ProjectFunding(BaseEntity):
    __tablename__ = "project_funding"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    
    round_type: Mapped[str] = mapped_column(String, nullable=False, default=ProjectFundingRoundType.PRE_SEED.value)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Optional list or array of investor names/entities
    investors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    
    project = relationship("Project", backref="funding_rounds")
