import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Float, JSON, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity

class Forecast(BaseEntity):
    __tablename__ = "forecasts"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )

    target_type: Mapped[str] = mapped_column(String, index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(index=True)
    
    forecast_type: Mapped[str] = mapped_column(String, index=True)
    
    prediction: Mapped[dict] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Requirement: "all outputs explicitly labeled as predictions"
    is_prediction: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    factors: Mapped[list] = mapped_column(JSON, default=list)

    __table_args__ = (
        Index("ix_forecasts_target", "target_type", "target_id"),
    )
