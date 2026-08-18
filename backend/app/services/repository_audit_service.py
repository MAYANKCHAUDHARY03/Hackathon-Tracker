import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.repository_audit import RepositoryAudit
from app.schemas.repository_audit import RepositoryAuditCreate

class RepositoryAuditService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def generate_audit(self, project_id: uuid.UUID) -> RepositoryAudit:
        """
        Simulates an asynchronous security and quality audit on the linked repository.
        """
        # Mocking an audit based on Phase 55 requirements
        audit_data = RepositoryAuditCreate(
            project_id=project_id,
            cyclomatic_complexity_score=8.5, # Lower is better, just a mock
            sast_vulnerabilities_count=2,
            guideline_adherence_score=92.5, # Out of 100
            sast_findings=[
                {"severity": "High", "file": "src/api/auth.ts", "issue": "Hardcoded secret key detected (simulated)"},
                {"severity": "Medium", "file": "src/components/List.tsx", "issue": "Potential XSS vulnerability in raw HTML rendering"}
            ],
            guideline_violations=[
                {"rule": "Missing docstrings", "file": "src/utils/helpers.ts"},
                {"rule": "Unused imports", "file": "src/pages/Dashboard.tsx"}
            ],
            audited_by_agent_id="code_auditor_agent_v1",
            status="COMPLETED"
        )

        audit = RepositoryAudit(**audit_data.model_dump())
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        
        return audit

    async def get_audits_for_project(self, project_id: uuid.UUID) -> list[RepositoryAudit]:
        result = await self.db.execute(
            select(RepositoryAudit)
            .where(RepositoryAudit.project_id == project_id)
            .order_by(RepositoryAudit.created_at.desc())
        )
        return list(result.scalars().all())
