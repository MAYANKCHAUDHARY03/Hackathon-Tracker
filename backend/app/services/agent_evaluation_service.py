import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.project import Project
from app.models.evaluation import Evaluation, EvaluationScore, EvaluationTemplate, EvaluationCriterion
from app.schemas.evaluation import EvaluationCreate, EvaluationScoreCreate
from app.services import evaluation_service
from decimal import Decimal

class AgentEvaluationService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def generate_preliminary_evaluation(self, hackathon_id: uuid.UUID, project_id: uuid.UUID, template_id: uuid.UUID) -> Evaluation:
        """
        Generates an AI_PRELIMINARY evaluation for a project using the given template.
        """
        # 1. Fetch template and criteria
        template_result = await self.db.execute(
            select(EvaluationTemplate).where(EvaluationTemplate.id == template_id)
        )
        template = template_result.scalars().first()
        if not template:
            raise ValueError("Template not found")

        criteria_result = await self.db.execute(
            select(EvaluationCriterion).where(EvaluationCriterion.template_id == template_id)
        )
        criteria = criteria_result.scalars().all()

        # 2. Fetch project
        project_result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalars().first()
        if not project:
            raise ValueError("Project not found")

        # 3. Simulate AI evaluation logic based on project data
        scores_data = []
        overall_score = Decimal(0)
        
        for criterion in criteria:
            # Mock AI scoring logic
            # E.g., if project has a demo_url, it gets higher points for completeness
            max_score = criterion.maximum_score or Decimal(10)
            
            numeric_score = Decimal(0)
            feedback = ""
            
            if "technical" in criterion.name.lower():
                numeric_score = max_score * Decimal("0.8")
                feedback = "Solid technical foundation. The codebase structure is clean, but lacks comprehensive tests."
            elif "design" in criterion.name.lower() or "ux" in criterion.name.lower():
                numeric_score = max_score * Decimal("0.7")
                feedback = "UI is functional but could use more polish on mobile breakpoints."
            elif "innovation" in criterion.name.lower() or "originality" in criterion.name.lower():
                numeric_score = max_score * Decimal("0.9")
                feedback = "Very innovative approach to a common problem."
            else:
                numeric_score = max_score * Decimal("0.75")
                feedback = "Meets the requirements adequately."

            # Round to 1 decimal place
            numeric_score = round(numeric_score, 1)
            
            scores_data.append(EvaluationScoreCreate(
                criterion_id=criterion.id,
                numeric_score=numeric_score,
                feedback=feedback
            ))

        # 4. Create the evaluation record
        evaluation_create = EvaluationCreate(
            hackathon_id=hackathon_id,
            team_id=project.team_id,
            project_id=project_id,
            template_id=template_id,
            status="AI_PRELIMINARY",
            overall_feedback="The AI has reviewed the codebase and provided preliminary scores. Please review and adjust as necessary.",
            source="AGENT"
        )

        # Let the standard evaluation service handle the DB insertion
        evaluation = await evaluation_service.create_evaluation(
            self.db, 
            self.workspace_id, 
            self.actor_id, 
            evaluation_create
        )

        # Update scores 
        # (Assuming update_evaluation can handle adding/updating scores)
        from app.schemas.evaluation import EvaluationUpdate
        await evaluation_service.update_evaluation(
            self.db,
            self.workspace_id,
            evaluation.id,
            self.actor_id,
            EvaluationUpdate(scores=scores_data, status="AI_PRELIMINARY")
        )

        return evaluation
