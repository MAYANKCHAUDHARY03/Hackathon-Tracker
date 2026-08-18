from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.cache import cache
from app.models.project import Project
from app.models.hackathon import Hackathon
from app.models.user import WorkspaceMembership
from app.models.impact import ProjectImpact
from app.schemas.observatory import ObservatoryStats

class ObservatoryService:
    @staticmethod
    @cache(expire=300)
    async def get_workspace_stats(workspace_id: UUID, db: AsyncSession) -> ObservatoryStats:
        # 1. Total projects
        projects_query = select(func.count()).select_from(Project).where(Project.workspace_id == workspace_id)
        total_projects = await db.scalar(projects_query) or 0
        
        # 2. Total participants
        participants_query = select(func.count()).select_from(WorkspaceMembership).where(WorkspaceMembership.workspace_id == workspace_id)
        total_participants = await db.scalar(participants_query) or 0
        
        # 3. Total hackathons
        hackathons_query = select(func.count()).select_from(Hackathon).where(Hackathon.workspace_id == workspace_id)
        total_hackathons = await db.scalar(hackathons_query) or 0
        
        # 4. Total impact metrics
        impact_query = select(
            func.sum(ProjectImpact.jobs_created),
            func.sum(ProjectImpact.funding_raised),
            func.sum(ProjectImpact.revenue_generated)
        ).where(ProjectImpact.workspace_id == workspace_id)
        
        impact_result = await db.execute(impact_query)
        jobs, funding, revenue = impact_result.one_or_none() or (0, 0.0, 0.0)
        
        return ObservatoryStats(
            total_projects=total_projects,
            total_participants=total_participants,
            total_hackathons=total_hackathons,
            total_jobs_created=jobs or 0,
            total_funding_raised=funding or 0.0,
            total_revenue_generated=revenue or 0.0
        )

    @staticmethod
    async def get_drilldown(workspace_id: UUID, level: str, db: AsyncSession):
        from app.schemas.observatory import DrillDownResponse, TrendNode, TimeSeriesPoint
        import random
        from datetime import datetime, timedelta
        
        # Mocking for Phase 64
        nodes = []
        if level == "technology":
            items = ["React", "Python", "Web3", "AI", "Cloud"]
        elif level == "geography":
            items = ["North America", "Europe", "Asia", "South America", "Africa"]
        elif level == "domain":
            items = ["Healthcare", "Finance", "Education", "Sustainability", "Logistics"]
        else:
            items = ["Item A", "Item B", "Item C", "Item D", "Item E"]
            
        today = datetime.utcnow()
        for item in items:
            timeseries = []
            for i in range(12):
                dt = today - timedelta(days=30*(11-i))
                timeseries.append(TimeSeriesPoint(
                    date=dt.strftime("%Y-%m"),
                    value=random.randint(10, 100)
                ))
                
            nodes.append(TrendNode(
                id=item.lower().replace(" ", "-"),
                name=item,
                value=random.randint(100, 1000),
                trend_percentage=random.uniform(-10.0, 50.0),
                time_series=timeseries
            ))
            
        return DrillDownResponse(level=level, nodes=nodes)
