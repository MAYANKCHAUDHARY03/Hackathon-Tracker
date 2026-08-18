import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.operations_center import OperationsCenterStatus, ActiveProgramStat, Alert
from app.models.hackathon import Hackathon
from app.models.team import Team
from app.models.user import User

class OperationsCenterService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def get_status(self) -> OperationsCenterStatus:
        # In a real implementation, this would aggregate from the event stream (Phase 47).
        # We will mock the AI alerts and combine with basic DB metrics for now.
        
        # 1. Active Programs
        stmt = select(Hackathon).where(Hackathon.workspace_id == self.workspace_id)
        result = await self.db.execute(stmt)
        hackathons = result.scalars().all()
        
        active_programs = []
        for h in hackathons:
            # Mocking stats for each program to simulate Phase 58 output
            active_programs.append(ActiveProgramStat(
                program_id=h.id,
                name=h.name,
                active_teams=12,
                pending_evaluations=4,
                at_risk_projects=1
            ))

        # 2. Mock Live AI Alerts (from copilots)
        live_alerts = [
            Alert(
                id=uuid.uuid4(),
                severity="CRITICAL",
                message="Evaluation backlog increasing by 40% in 'Global Innovation Challenge'",
                source="Organizer Copilot",
                timestamp=datetime.utcnow() - timedelta(minutes=5)
            ),
            Alert(
                id=uuid.uuid4(),
                severity="WARNING",
                message="3 projects approaching submission deadline with no README.",
                source="Project Copilot",
                timestamp=datetime.utcnow() - timedelta(minutes=15)
            ),
            Alert(
                id=uuid.uuid4(),
                severity="INFO",
                message="Mentor 'Dr. Sarah Chen' resolved 2 blockers.",
                source="Mentor Copilot",
                timestamp=datetime.utcnow() - timedelta(minutes=30)
            )
        ]

        return OperationsCenterStatus(
            total_active_programs=len(hackathons),
            total_active_users=150,  # Mocked
            total_pending_evaluations=sum(p.pending_evaluations for p in active_programs),
            critical_incidents=1,
            active_programs=active_programs,
            live_alerts=live_alerts
        )
