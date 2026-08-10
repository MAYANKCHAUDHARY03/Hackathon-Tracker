from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.models.project import Project, ProjectTechnology, Technology
from app.schemas.intelligence import EcosystemAnalyticsResponse, TechnologyAdoptionMetric, ProjectStatusMetric, ParticipationTrendMetric
from datetime import datetime, timezone
import uuid

class IntelligenceService:
    @staticmethod
    async def get_ecosystem_analytics(db: AsyncSession) -> EcosystemAnalyticsResponse:
        # Total projects
        total_projects_result = await db.execute(select(func.count(Project.id)))
        total_projects = total_projects_result.scalar() or 0

        # Total technologies
        total_technologies_result = await db.execute(select(func.count(Technology.id)))
        total_technologies = total_technologies_result.scalar() or 0

        # Top technologies
        top_tech_query = (
            select(
                Technology.name,
                Technology.category,
                func.count(ProjectTechnology.project_id).label('project_count')
            )
            .join(ProjectTechnology, Technology.id == ProjectTechnology.technology_id)
            .group_by(Technology.id)
            .order_by(func.count(ProjectTechnology.project_id).desc())
            .limit(10)
        )
        top_tech_result = await db.execute(top_tech_query)
        top_technologies = [
            TechnologyAdoptionMetric(
                technology_name=row.name,
                category=row.category,
                project_count=row.project_count
            )
            for row in top_tech_result.all()
        ]

        # Project status distribution
        status_query = (
            select(
                Project.status,
                func.count(Project.id).label('project_count')
            )
            .group_by(Project.status)
        )
        status_result = await db.execute(status_query)
        project_status_distribution = [
            ProjectStatusMetric(
                status=row.status or "unknown",
                project_count=row.project_count
            )
            for row in status_result.all()
        ]

        # Participation trends (group by YYYY-MM of created_at)
        # SQLite doesn't have TO_CHAR, PostgreSQL does. We can use strftime for SQLite, or extract for PG.
        # To be DB agnostic or simple, we'll use a text formulation depending on the DB, or just use string manipulation if it's SQLite. 
        # For simplicity, assuming SQLite here based on previous steps (or PG compatible).
        # Let's use func.substr(Project.created_at, 1, 7) for SQLite, or cast to string and substring.
        trend_query = (
            select(
                func.substr(func.cast(Project.created_at, text('TEXT')), 1, 7).label('period'),
                func.count(Project.id).label('project_count')
            )
            .group_by('period')
            .order_by('period')
            .limit(12)
        )
        try:
            trend_result = await db.execute(trend_query)
            participation_trends = [
                ParticipationTrendMetric(
                    period=row.period or "unknown",
                    project_count=row.project_count
                )
                for row in trend_result.all()
            ]
        except Exception:
            # Fallback if DB doesn't support the above
            participation_trends = []

        return EcosystemAnalyticsResponse(
            total_projects=total_projects,
            total_technologies=total_technologies,
            top_technologies=top_technologies,
            project_status_distribution=project_status_distribution,
            participation_trends=participation_trends
        )
