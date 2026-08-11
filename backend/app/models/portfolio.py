from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
from .base import Base

class PortfolioProject(Base):
    __tablename__ = "portfolio_projects"
    
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    
    owner_id = Column(UUID(as_uuid=True), nullable=False) # ID of user, team, or startup
    owner_type = Column(String, nullable=False, default="user") # "user", "team", "startup"
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_public = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    projects = relationship("Project", secondary="portfolio_projects", backref="portfolios")
