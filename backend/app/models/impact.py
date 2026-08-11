import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON, Integer, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity

class CustomMetric(BaseEntity):
    __tablename__ = "custom_metrics"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    unit: Mapped[str] = mapped_column(String) # e.g., 'count', 'USD'

class ProjectImpact(BaseEntity):
    __tablename__ = "project_impacts"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), unique=True, index=True
    )
    
    # Funnel Stage
    stage: Mapped[str] = mapped_column(String, default="Participation", index=True)
    
    # Custom metrics stored as JSON { "metric_name": value }
    custom_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Standard metrics
    jobs_created: Mapped[int] = mapped_column(Integer, default=0)
    funding_raised: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_generated: Mapped[float] = mapped_column(Float, default=0.0)
