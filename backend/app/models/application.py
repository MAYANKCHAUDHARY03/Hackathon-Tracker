from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime

class ApplicationForm(Base):
    __tablename__ = "application_forms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hackathon_id = Column(String, ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    schema_json = Column(JSON, nullable=False, default=list) # List of fields
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hackathon = relationship("Hackathon", back_populates="application_forms")
    submissions = relationship("ApplicationSubmission", back_populates="form", cascade="all, delete-orphan")

class ApplicationSubmission(Base):
    __tablename__ = "application_submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id = Column(String, ForeignKey("application_forms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    data_json = Column(JSON, nullable=False, default=dict)
    status = Column(String, default="pending") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    form = relationship("ApplicationForm", back_populates="submissions")
    user = relationship("User")
