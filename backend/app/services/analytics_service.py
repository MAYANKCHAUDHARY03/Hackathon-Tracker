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
from app.models.organization import Organization
from app.models.evaluation import EvaluationScore, Evaluation
from app.schemas.analytics import WorkspaceAnalyticsSummary, AnalyticsOverview, AnalyticsDemographics, AnalyticsEvaluations, ScoreDistribution

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

    async def get_overview(self, workspace_id: UUID) -> AnalyticsOverview:
        total_users = await self.session.scalar(
            select(func.count()).select_from(WorkspaceMembership).where(WorkspaceMembership.workspace_id == workspace_id)
        )
        total_teams = await self.session.scalar(
            select(func.count()).select_from(Team).where(Team.workspace_id == workspace_id)
        )
        total_projects = await self.session.scalar(
            select(func.count()).select_from(Project).where(Project.workspace_id == workspace_id)
        )
        # Mock submissions count based on projects for now
        return AnalyticsOverview(
            total_users=total_users or 0,
            total_teams=total_teams or 0,
            total_projects=total_projects or 0,
            total_submissions=total_projects or 0
        )

    async def get_demographics(self, workspace_id: UUID) -> AnalyticsDemographics:
        # Mock demographics since user profiles are not fully fleshed out with skills in DB yet
        return AnalyticsDemographics(
            skills_distribution={"React": 45, "Python": 32, "Node.js": 28, "UI/UX": 15},
            roles_distribution={"Frontend": 40, "Backend": 30, "Fullstack": 20, "Designer": 10}
        )

    async def get_evaluations(self, workspace_id: UUID) -> AnalyticsEvaluations:
        # Get all evaluation scores for the workspace
        stmt = (
            select(EvaluationScore.score)
            .join(Evaluation, Evaluation.id == EvaluationScore.evaluation_id)
            .where(Evaluation.workspace_id == workspace_id)
        )
        scores = (await self.session.scalars(stmt)).all()
        
        total_evals = len(scores)
        avg_score = sum(scores) / total_evals if total_evals > 0 else 0
        
        dist = ScoreDistribution(range_0_20=0, range_21_40=0, range_41_60=0, range_61_80=0, range_81_100=0)
        for s in scores:
            if s <= 20: dist.range_0_20 += 1
            elif s <= 40: dist.range_21_40 += 1
            elif s <= 60: dist.range_41_60 += 1
            elif s <= 80: dist.range_61_80 += 1
            else: dist.range_81_100 += 1
            
        return AnalyticsEvaluations(
            average_score=round(avg_score, 1),
            total_evaluations=total_evals,
            score_distribution=dist
        )

    async def get_ecosystem_summary(self) -> dict:
        """
        Phase 27 - Platform Governance:
        Returns ecosystem-level analytics, aggregating data across multiple organizations.
        Strictly enforces that data from organizations with ecosystem_opt_in=False
        is anonymized (e.g., project/user details scrubbed), while opted-in orgs
        can contribute deeper trends.
        """
        # Fetch all organizations and their opt-in status
        orgs = (await self.session.execute(select(Organization.id, Organization.name, Organization.ecosystem_opt_in))).all()
        
        ecosystem_stats = {
            "total_organizations": len(orgs),
            "opted_in_organizations": sum(1 for o in orgs if o.ecosystem_opt_in),
            "opted_out_organizations": sum(1 for o in orgs if not o.ecosystem_opt_in),
            "aggregated_data": {
                "total_projects": 0,
                "total_users": 0
            },
            "public_trends": []
        }
        
        # Calculate cross-org stats
        for org in orgs:
            # Get basic aggregates per org (which is safe even if opted out as long as it's just a count)
            # In a real system, you might not even expose the breakdown per opted-out org.
            
            # Since workspaces belong to organizations, we get all workspaces for the org
            from app.models.workspace import Workspace
            workspaces = (await self.session.execute(select(Workspace.id).where(Workspace.organization_id == org.id))).scalars().all()
            
            org_projects = 0
            org_users = 0
            for ws_id in workspaces:
                org_projects += (await self.session.scalar(select(func.count()).select_from(Project).where(Project.workspace_id == ws_id))) or 0
                org_users += (await self.session.scalar(select(func.count()).select_from(WorkspaceMembership).where(WorkspaceMembership.workspace_id == ws_id))) or 0
                
            ecosystem_stats["aggregated_data"]["total_projects"] += org_projects
            ecosystem_stats["aggregated_data"]["total_users"] += org_users
            
            # If opted in, they contribute to detailed public trends
            if org.ecosystem_opt_in:
                ecosystem_stats["public_trends"].append({
                    "organization_name": org.name,
                    "projects": org_projects,
                    "users": org_users
                })
            else:
                ecosystem_stats["public_trends"].append({
                    "organization_name": "[ANONYMIZED]",
                    "projects": "[HIDDEN]",
                    "users": "[HIDDEN]"
                })
                
        return ecosystem_stats
