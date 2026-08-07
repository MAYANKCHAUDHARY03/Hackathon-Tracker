from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from datetime import datetime

from app.models.feedback import FeedbackType

class FeedbackBase(BaseModel):
    type: FeedbackType
    description: str
    url: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
