from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

class ForecastBase(BaseModel):
    target_type: str = Field(..., description="Type of entity being forecasted")
    target_id: UUID
    forecast_type: str = Field(..., description="E.g., success_probability, engagement_drop")
    prediction: Dict[str, Any] = Field(..., description="Prediction output details")
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_prediction: bool = Field(True, description="Always true. Forecasts are explicitly labeled as predictions.")
    factors: List[str] = Field(default_factory=list, description="Key factors driving the prediction")

class ForecastCreate(ForecastBase):
    pass

class ForecastResponse(ForecastBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
