import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity

class RepositoryAudit(BaseEntity):
    __tablename__ = "repository_audits"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Audit metrics
    cyclomatic_complexity_score = Column(Float, nullable=True)
    sast_vulnerabilities_count = Column(Integer, default=0)
    guideline_adherence_score = Column(Float, nullable=True)
    
    # Detailed findings stored as JSON
    sast_findings = Column(JSON, default=list)
    guideline_violations = Column(JSON, default=list)
    
    # Agent executing the audit
    audited_by_agent_id = Column(String, nullable=True)
    status = Column(String, default="COMPLETED") # PENDING, COMPLETED, FAILED
    
    project = relationship("Project")
