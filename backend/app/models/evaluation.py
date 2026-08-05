import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Enum, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseEntity
import enum

class ScoringMethod(str, enum.Enum):
    weighted = "weighted"
    points = "points"
    pass_fail = "pass_fail"

class EvaluationStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    locked = "locked"
    archived = "archived"

class EvaluationTemplate(BaseEntity):
    __tablename__ = "evaluation_templates"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_rounds.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    scoring_method = Column(Enum(ScoringMethod, name="scoring_method_enum"), default=ScoringMethod.points, nullable=False)
    maximum_total_score = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum(EvaluationStatus, name="eval_template_status_enum"), default=EvaluationStatus.draft, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class EvaluationCriterion(BaseEntity):
    __tablename__ = "evaluation_criteria"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    weight = Column(Numeric(5, 2), nullable=True) # Percentage weight for weighted scoring
    maximum_score = Column(Numeric(10, 2), nullable=True) # Max points for points scoring
    position = Column(Integer, default=0, nullable=False)
    is_required = Column(Boolean, default=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class Evaluation(BaseEntity):
    __tablename__ = "evaluations"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False, index=True)
    round_id = Column(UUID(as_uuid=True), ForeignKey("hackathon_rounds.id", ondelete="SET NULL"), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluator_person_id = Column(UUID(as_uuid=True), ForeignKey("people.id", ondelete="SET NULL"), nullable=True)
    evaluator_name_snapshot = Column(String, nullable=True)
    status = Column(Enum(EvaluationStatus, name="evaluation_status_enum"), default=EvaluationStatus.draft, nullable=False)
    total_score = Column(Numeric(10, 2), nullable=True)
    maximum_score = Column(Numeric(10, 2), nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)
    overall_feedback = Column(String, nullable=True)
    source = Column(String, nullable=True)
    template_snapshot = Column(JSON, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

class EvaluationScore(BaseEntity):
    __tablename__ = "evaluation_scores"

    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_criteria.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_name_snapshot = Column(String, nullable=True)
    weight_snapshot = Column(Numeric(5, 2), nullable=True)
    maximum_score_snapshot = Column(Numeric(10, 2), nullable=True)
    numeric_score = Column(Numeric(10, 2), nullable=True)
    pass_value = Column(Boolean, nullable=True)
    feedback = Column(String, nullable=True)
