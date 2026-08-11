import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.evaluation import EvaluationTemplate, EvaluationCriterion, Evaluation, EvaluationScore, ScoringMethod, EvaluationStatus
from app.schemas.evaluation import EvaluationTemplateCreate, EvaluationTemplateUpdate, EvaluationCriterionCreate, EvaluationCriterionUpdate, EvaluationCreate, EvaluationUpdate
from sqlalchemy.orm import selectinload
from decimal import Decimal
from datetime import datetime, timezone

async def create_template(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: EvaluationTemplateCreate) -> EvaluationTemplate:
    template = EvaluationTemplate(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template

async def get_templates(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[EvaluationTemplate]:
    query = select(EvaluationTemplate).where(
        EvaluationTemplate.workspace_id == workspace_id,
        EvaluationTemplate.hackathon_id == hackathon_id,
        EvaluationTemplate.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_template(db: AsyncSession, workspace_id: uuid.UUID, template_id: uuid.UUID) -> EvaluationTemplate:
    query = select(EvaluationTemplate).where(
        EvaluationTemplate.workspace_id == workspace_id,
        EvaluationTemplate.id == template_id
    )
    result = await db.execute(query)
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Load criteria
    criteria_query = select(EvaluationCriterion).where(
        EvaluationCriterion.template_id == template_id,
        EvaluationCriterion.archived_at.is_(None)
    ).order_by(EvaluationCriterion.position)
    
    criteria_result = await db.execute(criteria_query)
    template.criteria = criteria_result.scalars().all()
    
    return template

async def create_criterion(db: AsyncSession, workspace_id: uuid.UUID, template_id: uuid.UUID, data: EvaluationCriterionCreate) -> EvaluationCriterion:
    template = await get_template(db, workspace_id, template_id)
    if template.status == EvaluationStatus.locked:
        raise HTTPException(status_code=400, detail="Cannot add criteria to a locked template")
        
    criterion = EvaluationCriterion(
        workspace_id=workspace_id,
        template_id=template_id,
        **data.model_dump()
    )
    db.add(criterion)
    await db.commit()
    await db.refresh(criterion)
    return criterion

def calculate_evaluation(template: EvaluationTemplate, criteria: list[EvaluationCriterion], scores: list[EvaluationScore]) -> tuple[Decimal, Decimal, Decimal]:
    total_score = Decimal(0)
    max_score = Decimal(0)
    percentage = Decimal(0)
    
    if template.scoring_method == ScoringMethod.points:
        for score in scores:
            criterion = next((c for c in criteria if c.id == score.criterion_id), None)
            if criterion and criterion.maximum_score:
                max_score += criterion.maximum_score
                if score.numeric_score is not None:
                    total_score += score.numeric_score
        
        if max_score > 0:
            percentage = (total_score / max_score) * 100

    elif template.scoring_method == ScoringMethod.weighted:
        for score in scores:
            criterion = next((c for c in criteria if c.id == score.criterion_id), None)
            if criterion and criterion.maximum_score and criterion.weight:
                # Add to maximum possible score (total weight should ideally be 100)
                max_score += criterion.maximum_score * (criterion.weight / Decimal(100))
                
                if score.numeric_score is not None:
                    weighted_score = (score.numeric_score / criterion.maximum_score) * criterion.weight
                    total_score += weighted_score
        
        if max_score > 0:
            percentage = (total_score / max_score) * 100
            
    elif template.scoring_method == ScoringMethod.pass_fail:
        passes = 0
        total = 0
        for score in scores:
            criterion = next((c for c in criteria if c.id == score.criterion_id), None)
            if criterion:
                total += 1
                if score.pass_value:
                    passes += 1
        
        total_score = Decimal(passes)
        max_score = Decimal(total)
        if total > 0:
            percentage = (Decimal(passes) / Decimal(total)) * 100

    return total_score, max_score, percentage

async def create_evaluation(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: EvaluationCreate) -> Evaluation:
    template = await get_template(db, workspace_id, data.template_id)
    
    evaluation = Evaluation(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    return evaluation

async def update_evaluation(db: AsyncSession, workspace_id: uuid.UUID, evaluation_id: uuid.UUID, user_id: uuid.UUID, data: EvaluationUpdate) -> Evaluation:
    query = select(Evaluation).where(
        Evaluation.workspace_id == workspace_id,
        Evaluation.id == evaluation_id
    )
    result = await db.execute(query)
    evaluation = result.scalars().first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
        
    if evaluation.status == EvaluationStatus.locked:
        raise HTTPException(status_code=400, detail="Cannot modify a locked evaluation")
        
    if data.overall_feedback is not None:
        evaluation.overall_feedback = data.overall_feedback
        
    template = await get_template(db, workspace_id, evaluation.template_id)
    criteria = template.criteria
    
    if data.scores:
        # Delete existing scores
        delete_query = select(EvaluationScore).where(EvaluationScore.evaluation_id == evaluation_id)
        existing = await db.execute(delete_query)
        for s in existing.scalars().all():
            await db.delete(s)
            
        new_scores = []
        for s in data.scores:
            c = next((c for c in criteria if c.id == s.criterion_id), None)
            score = EvaluationScore(
                evaluation_id=evaluation_id,
                criterion_id=s.criterion_id,
                criterion_name_snapshot=c.name if c else None,
                weight_snapshot=c.weight if c else None,
                maximum_score_snapshot=c.maximum_score if c else None,
                numeric_score=s.numeric_score,
                pass_value=s.pass_value,
                feedback=s.feedback
            )
            db.add(score)
            new_scores.append(score)
            
        evaluation.scores = new_scores
        
        total, max_score, pct = calculate_evaluation(template, criteria, new_scores)
        evaluation.total_score = total
        evaluation.maximum_score = max_score
        evaluation.percentage = pct
        
    if data.status:
        evaluation.status = data.status
        if data.status == EvaluationStatus.locked:
            evaluation.locked_at = datetime.now(timezone.utc)
            
        if data.status in [EvaluationStatus.completed, EvaluationStatus.locked] and not evaluation.evaluated_at:
            evaluation.evaluated_at = datetime.now(timezone.utc)
            
    evaluation.updated_by = user_id
    await db.commit()
    await db.refresh(evaluation)
    
    # Reload scores
    scores_query = select(EvaluationScore).where(EvaluationScore.evaluation_id == evaluation_id)
    s_result = await db.execute(scores_query)
    evaluation.scores = s_result.scalars().all()
    
    if data.status in [EvaluationStatus.completed, EvaluationStatus.locked]:
        from app.services.event_service import EventService
        from app.schemas.event import EventCreate
        event_svc = EventService(db)
        await event_svc.publish(EventCreate(
            workspace_id=workspace_id,
            actor_id=user_id,
            entity_type="evaluation",
            entity_id=str(evaluation.id),
            event_type="evaluation_completed",
            source="api",
            metadata_json={
                "submission_id": str(evaluation.submission_id) if evaluation.submission_id else None,
                "template_id": str(evaluation.template_id),
                "total_score": float(evaluation.total_score) if evaluation.total_score else None
            }
        ))
    
    return evaluation
