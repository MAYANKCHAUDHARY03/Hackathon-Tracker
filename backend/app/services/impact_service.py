from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.impact import CustomMetric, ProjectImpact
from app.models.project import Project
from app.schemas.impact import CustomMetricCreate, ProjectImpactUpdate, ProjectImpactResponse, CustomMetricResponse

class ImpactService:
    @staticmethod
    async def create_custom_metric(
        workspace_id: UUID,
        data: CustomMetricCreate,
        db: AsyncSession
    ) -> CustomMetricResponse:
        metric = CustomMetric(
            workspace_id=workspace_id,
            name=data.name,
            description=data.description,
            unit=data.unit
        )
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        return CustomMetricResponse.model_validate(metric)

    @staticmethod
    async def list_custom_metrics(
        workspace_id: UUID,
        db: AsyncSession
    ) -> List[CustomMetricResponse]:
        query = select(CustomMetric).where(CustomMetric.workspace_id == workspace_id)
        result = await db.execute(query)
        metrics = result.scalars().all()
        return [CustomMetricResponse.model_validate(m) for m in metrics]

    @staticmethod
    async def list_project_impacts(
        workspace_id: UUID,
        db: AsyncSession
    ) -> List[ProjectImpactResponse]:
        query = select(ProjectImpact).where(ProjectImpact.workspace_id == workspace_id)
        result = await db.execute(query)
        impacts = result.scalars().all()
        return [ProjectImpactResponse.model_validate(m) for m in impacts]

    @staticmethod
    async def update_project_impact(
        workspace_id: UUID,
        project_id: UUID,
        data: ProjectImpactUpdate,
        db: AsyncSession
    ) -> ProjectImpactResponse:
        # Check project exists
        project_query = select(Project).where(
            Project.id == project_id, 
            Project.workspace_id == workspace_id
        )
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError("Project not found")

        # Fetch or create ProjectImpact
        impact_query = select(ProjectImpact).where(ProjectImpact.project_id == project_id)
        result = await db.execute(impact_query)
        impact = result.scalar_one_or_none()

        if not impact:
            impact = ProjectImpact(
                workspace_id=workspace_id,
                project_id=project_id,
                stage="Participation"
            )
            db.add(impact)

        # Update fields
        if data.stage is not None:
            impact.stage = data.stage
        if data.jobs_created is not None:
            impact.jobs_created = data.jobs_created
        if data.funding_raised is not None:
            impact.funding_raised = data.funding_raised
        if data.revenue_generated is not None:
            impact.revenue_generated = data.revenue_generated
        
        if data.custom_metrics is not None:
            # Merge dictionary safely
            current_metrics = (impact.custom_metrics or {}).copy()
            current_metrics.update(data.custom_metrics)
            impact.custom_metrics = current_metrics
            
        await db.commit()
        await db.refresh(impact)
        return ProjectImpactResponse.model_validate(impact)

    @staticmethod
    async def get_funnel_metrics(
        workspace_id: UUID,
        db: AsyncSession
    ) -> dict:
        from sqlalchemy import func
        from app.models.user import WorkspaceMembership
        
        # 1. Participation = Total Workspace Members
        part_query = select(func.count(WorkspaceMembership.id)).where(WorkspaceMembership.workspace_id == workspace_id)
        part_result = await db.execute(part_query)
        participation = part_result.scalar() or 0
        
        # 2. Projects = Total Projects
        proj_query = select(func.count(Project.id)).where(Project.workspace_id == workspace_id)
        proj_result = await db.execute(proj_query)
        projects = proj_result.scalar() or 0
        
        # Now use ProjectImpact for other stages
        # "Participation", "Project", "Prototype", "Pilot", "Deployment", "Startup", "Impact"
        stmt = select(ProjectImpact.stage, func.count(ProjectImpact.id)).where(
            ProjectImpact.workspace_id == workspace_id
        ).group_by(ProjectImpact.stage)
        
        result = await db.execute(stmt)
        stage_counts = {row[0].lower(): row[1] for row in result.all()}
        
        jobs_stmt = select(func.sum(ProjectImpact.jobs_created)).where(
            ProjectImpact.workspace_id == workspace_id
        )
        jobs_result = await db.execute(jobs_stmt)
        total_jobs = jobs_result.scalar() or 0
        
        # Calculate stages (cascade down)
        startups = stage_counts.get("startup", 0)
        deployments = stage_counts.get("deployment", 0) + startups
        pilots = stage_counts.get("pilot", 0) + deployments
        prototypes = stage_counts.get("prototype", 0) + pilots
        
        return {
            "participation": participation,
            "projects": projects,
            "prototypes": prototypes,
            "pilots": pilots,
            "deployments": deployments,
            "startups": startups,
            "jobs": total_jobs
        }
