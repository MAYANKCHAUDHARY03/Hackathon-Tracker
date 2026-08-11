from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum
from .base import Base

class MatchOpportunityType(str, enum.Enum):
    investor = "investor"
    mentor = "mentor"
    grant = "grant"
    partner = "partner"

class MatchOpportunity(Base):
    __tablename__ = "match_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    opportunity_type = Column(String, nullable=False) # e.g. "investor", "mentor", "grant"
    
    # Provider of the opportunity (could be an organization, user, etc. For simplicity, just an ID)
    provider_id = Column(UUID(as_uuid=True), nullable=True)
    
    tags = Column(JSON, default=list) # e.g. ["fintech", "seed", "AI"]
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class MatchProfile(Base):
    __tablename__ = "match_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    
    entity_type = Column(String, nullable=False) # "team", "project", "user"
    entity_id = Column(String, nullable=False, index=True)
    
    tags = Column(JSON, default=list) # e.g. ["fintech", "seed", "AI"]
    needs = Column(JSON, default=list) # e.g. ["funding", "mentorship"]
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class MatchRecommendation(Base):
    __tablename__ = "match_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    
    profile_id = Column(UUID(as_uuid=True), ForeignKey("match_profiles.id"), nullable=False)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("match_opportunities.id"), nullable=False)
    
    score = Column(Integer, nullable=False, default=0) # Match score 0-100
    status = Column(String, nullable=False, default="suggested") # "suggested", "accepted", "rejected"
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("MatchProfile")
    opportunity = relationship("MatchOpportunity")
