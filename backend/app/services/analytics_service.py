from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from app.models.hackathon import Hackathon
from app.models.project import Project
from app.models.team import Team
from app.models.user import WorkspaceMembership
from app.models.kanban import Task, KanbanBoard, ColumnSemanticType, KanbanColumn
from app.models.activity import ActivityEvent
from app.schemas.analytics import WorkspaceAnalyticsSummary

class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_workspace_summary(self, workspace_id: UUID) -> WorkspaceAnalyticsSummary:
        # Total Hackathons
        total_hackathons = await self.session.scalar(
            select(func.count()).select_from(Hackathon).where(Hackathon.workspace_id == workspace_id)
        )
        
        # Active Hackathons
        active_hackathons = await self.session.scalar(
            select(func.count()).select_from(Hackathon).where(
                and_(Hackathon.workspace_id == workspace_id, Hackathon.status == "active")
            )
        )
        
        # Total Projects
        total_projects = await self.session.scalar(
            select(func.count()).select_from(Project).where(Project.workspace_id == workspace_id)
        )
        
        # Total Teams
        total_teams = await self.session.scalar(
            select(func.count()).select_from(Team).where(Team.workspace_id == workspace_id)
        )
        
        # Total Users in Workspace
        total_users = await self.session.scalar(
            select(func.count()).select_from(WorkspaceMembership).where(WorkspaceMembership.workspace_id == workspace_id)
        )
        
        # Tasks (Join Task -> Column -> Board)
        tasks_stmt = (
            select(KanbanColumn.semantic_type, func.count(Task.id))
            .select_from(Task)
            .join(KanbanColumn, Task.column_id == KanbanColumn.id)
            .join(KanbanBoard, Task.board_id == KanbanBoard.id)
            .where(KanbanBoard.workspace_id == workspace_id)
            .group_by(KanbanColumn.semantic_type)
        )
        
        task_stats = (await self.session.execute(tasks_stmt)).all()
        tasks_completed = sum(count for stype, count in task_stats if stype == ColumnSemanticType.DONE.value)
        tasks_pending = sum(count for stype, count in task_stats if stype != ColumnSemanticType.DONE.value)
        
        # Recent Activity (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_activity_count = await self.session.scalar(
            select(func.count()).select_from(ActivityEvent).where(
                and_(
                    ActivityEvent.workspace_id == workspace_id,
                    ActivityEvent.created_at >= thirty_days_ago
                )
            )
        )
        
        return WorkspaceAnalyticsSummary(
            total_hackathons=total_hackathons or 0,
            active_hackathons=active_hackathons or 0,
            total_projects=total_projects or 0,
            total_teams=total_teams or 0,
            total_users=total_users or 0,
            tasks_completed=tasks_completed,
            tasks_pending=tasks_pending,
            recent_activity_count=recent_activity_count or 0
        )
