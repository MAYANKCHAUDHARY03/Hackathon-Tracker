from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
import uuid

from app.models.base import BaseEntity

class FeedbackType(str, enum.Enum):
    BUG = "Bug"
    FRICTION = "Friction"
    REQUEST = "Request"

class Feedback(BaseEntity):
    __tablename__ = "feedback"

    type = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", backref="feedbacks")
