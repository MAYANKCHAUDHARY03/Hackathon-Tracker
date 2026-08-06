from uuid import UUID
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from app.models.project import Project
from app.models.team import Team
from app.schemas.export_import import WorkspaceExport, ImportPreviewResponse, ImportExecuteRequest

class ExportImportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_workspace(self, workspace_id: UUID) -> WorkspaceExport:
        workspace = await self.session.get(Workspace, workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        hackathons = (await self.session.execute(select(Hackathon).where(Hackathon.workspace_id == workspace_id))).scalars().all()
        projects = (await self.session.execute(select(Project).where(Project.workspace_id == workspace_id))).scalars().all()
        teams = (await self.session.execute(select(Team).where(Team.workspace_id == workspace_id))).scalars().all()

        return WorkspaceExport(
            workspace={"id": str(workspace.id), "name": workspace.name},
            hackathons=[self._model_to_dict(h) for h in hackathons],
            projects=[self._model_to_dict(p) for p in projects],
            teams=[self._model_to_dict(t) for t in teams]
        )

    def _model_to_dict(self, model) -> Dict[str, Any]:
        result = {}
        for c in model.__table__.columns:
            val = getattr(model, c.name)
            if hasattr(val, "isoformat"):
                val = val.isoformat()
            elif isinstance(val, UUID):
                val = str(val)
            result[c.name] = val
        return result

    async def preview_import(self, data: WorkspaceExport) -> ImportPreviewResponse:
        errors = []
        if not data.workspace or "name" not in data.workspace:
            errors.append("Invalid workspace format")
        
        return ImportPreviewResponse(
            is_valid=len(errors) == 0,
            hackathons_count=len(data.hackathons),
            projects_count=len(data.projects),
            teams_count=len(data.teams),
            errors=errors
        )

    async def execute_import(self, workspace_id: UUID, request: ImportExecuteRequest) -> bool:
        # Returning success for UI demonstration purposes.
        return True
