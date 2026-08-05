from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, and_, func, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hackathon import Hackathon
from app.schemas.dashboard import DashboardSummaryResponse

class DashboardService:
    @staticmethod
    async def get_dashboard_summary(db: AsyncSession, workspace_id: UUID) -> DashboardSummaryResponse:
        now = datetime.now(timezone.utc)
        
        # Base condition for non-archived in the workspace
        base_conditions = and_(
            Hackathon.workspace_id == workspace_id,
            Hackathon.archived_at.is_(None)
        )
        
        # 1. Get counts
        # Active: start_date <= now and end_date >= now
        # Upcoming: start_date > now
        # Completed: end_date < now
        count_stmt = select(
            func.count().label("total"),
            func.sum(case((and_(Hackathon.start_date <= now, Hackathon.end_date >= now), 1), else_=0)).label("active"),
            func.sum(case((Hackathon.start_date > now, 1), else_=0)).label("upcoming"),
            func.sum(case((Hackathon.end_date < now, 1), else_=0)).label("completed"),
        ).where(base_conditions)
        
        count_result = await db.execute(count_stmt)
        counts = count_result.one()
        
        total_non_archived = counts.total or 0
        total_active = int(counts.active or 0)
        total_upcoming = int(counts.upcoming or 0)
        total_completed = int(counts.completed or 0)
        
        # 2. Nearest upcoming event
        nearest_stmt = (
            select(Hackathon)
            .where(and_(base_conditions, Hackathon.start_date > now))
            .order_by(asc(Hackathon.start_date))
            .limit(1)
        )
        nearest_result = await db.execute(nearest_stmt)
        nearest_upcoming = nearest_result.scalar_one_or_none()
        
        # 3. Upcoming deadlines (nearest deadlines for non-completed hackathons)
        deadlines_stmt = (
            select(Hackathon)
            .where(and_(base_conditions, Hackathon.end_date >= now))
            .order_by(asc(Hackathon.registration_deadline))
            .limit(5)
        )
        deadlines_result = await db.execute(deadlines_stmt)
        upcoming_deadlines = list(deadlines_result.scalars().all())
        
        # 4. Recently updated
        recent_stmt = (
            select(Hackathon)
            .where(base_conditions)
            .order_by(desc(Hackathon.updated_at))
            .limit(5)
        )
        recent_result = await db.execute(recent_stmt)
        recently_updated = list(recent_result.scalars().all())
        
        return DashboardSummaryResponse(
            total_active=total_active,
            total_upcoming=total_upcoming,
            total_completed=total_completed,
            total_non_archived=total_non_archived,
            upcoming_deadlines=upcoming_deadlines,
            nearest_upcoming_event=nearest_upcoming,
            recently_updated=recently_updated
        )
