from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List

class EvaluationCriterionBase(BaseModel):
    name: str
    description: Optional[str] = None
    weight: Optional[Decimal] = None
    maximum_score: Optional[Decimal] = None
    position: int = 0
    is_required: bool = True

class EvaluationCriterionCreate(EvaluationCriterionBase):
    pass

class EvaluationCriterionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[Decimal] = None
    maximum_score: Optional[Decimal] = None
    position: Optional[int] = None
    is_required: Optional[bool] = None

class EvaluationCriterionResponse(EvaluationCriterionBase):
    id: UUID
    template_id: UUID
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvaluationTemplateBase(BaseModel):
    hackathon_id: UUID
    round_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    scoring_method: str = "points"
    maximum_total_score: Optional[Decimal] = None
    status: str = "draft"

class EvaluationTemplateCreate(EvaluationTemplateBase):
    pass

class EvaluationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scoring_method: Optional[str] = None
    maximum_total_score: Optional[Decimal] = None
    status: Optional[str] = None

class EvaluationTemplateResponse(EvaluationTemplateBase):
    id: UUID
    workspace_id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    criteria: List[EvaluationCriterionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class EvaluationScoreBase(BaseModel):
    criterion_id: UUID
    numeric_score: Optional[Decimal] = None
    pass_value: Optional[bool] = None
    feedback: Optional[str] = None

class EvaluationScoreCreate(EvaluationScoreBase):
    pass

class EvaluationScoreResponse(EvaluationScoreBase):
    id: UUID
    evaluation_id: UUID
    criterion_name_snapshot: Optional[str] = None
    weight_snapshot: Optional[Decimal] = None
    maximum_score_snapshot: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EvaluationBase(BaseModel):
    hackathon_id: UUID
    round_id: Optional[UUID] = None
    team_id: UUID
    project_id: Optional[UUID] = None
    template_id: UUID
    evaluator_person_id: Optional[UUID] = None
    status: str = "draft"
    overall_feedback: Optional[str] = None
    source: Optional[str] = None

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationUpdate(BaseModel):
    status: Optional[str] = None
    overall_feedback: Optional[str] = None
    scores: Optional[List[EvaluationScoreCreate]] = None

class EvaluationResponse(EvaluationBase):
    id: UUID
    workspace_id: UUID
    evaluator_name_snapshot: Optional[str] = None
    total_score: Optional[Decimal] = None
    maximum_score: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    evaluated_at: Optional[datetime] = None
    locked_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    scores: List[EvaluationScoreResponse] = []

    model_config = ConfigDict(from_attributes=True)
