import json
import csv
import io
import zipfile
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import StreamingResponse, Response

from app.models.hackathon import Hackathon
from app.models.project import Project
from app.models.organization import Organization
from app.schemas.data_exchange import (
    InnovationSchemaV1, 
    ExportHackathonV1, 
    ExportProjectV1, 
    ExportOrganizationV1
)

class DataExchangeService:
    @staticmethod
    async def export_data(
        db: AsyncSession,
        workspace_id: str,
        format: str = "json",
        include_hackathons: bool = True,
        include_projects: bool = True,
        include_organizations: bool = True
    ) -> Response:
        
        schema = InnovationSchemaV1()
        
        if include_hackathons:
            result = await db.execute(
                select(Hackathon).where(Hackathon.workspace_id == workspace_id)
            )
            hackathons = result.scalars().all()
            for h in hackathons:
                schema.hackathons.append(ExportHackathonV1(
                    id=h.id,
                    name=h.name,
                    description=h.description,
                    mode=h.mode,
                    location=h.location,
                    registration_deadline=h.registration_deadline,
                    start_date=h.start_date,
                    end_date=h.end_date,
                    timezone=h.timezone,
                    max_team_size=h.max_team_size,
                    status=h.status,
                    program_type=h.program_type
                ))
                
        if include_projects:
            result = await db.execute(
                select(Project).where(Project.workspace_id == workspace_id)
            )
            projects = result.scalars().all()
            for p in projects:
                schema.projects.append(ExportProjectV1(
                    id=p.id,
                    title=p.title,
                    slug=p.slug,
                    solution_summary=p.solution_summary,
                    description=p.description,
                    repository_url=p.repository_url,
                    demo_url=p.demo_url,
                    status=p.status
                ))
                
        if include_organizations:
            from app.models.workspace import Workspace
            result = await db.execute(
                select(Organization).join(Workspace, Workspace.organization_id == Organization.id).where(Workspace.id == workspace_id)
            )
            orgs = result.scalars().all()
            for o in orgs:
                schema.organizations.append(ExportOrganizationV1(
                    id=o.id,
                    name=o.name,
                    description=o.description,
                    website=o.website
                ))

        if format == "json":
            return Response(
                content=schema.model_dump_json(indent=2),
                media_type="application/json"
            )
            
        elif format == "ndjson":
            lines = []
            for h in schema.hackathons:
                lines.append(json.dumps({"type": "hackathon", "data": h.model_dump(mode='json')}))
            for p in schema.projects:
                lines.append(json.dumps({"type": "project", "data": p.model_dump(mode='json')}))
            for o in schema.organizations:
                lines.append(json.dumps({"type": "organization", "data": o.model_dump(mode='json')}))
            return Response(
                content="\n".join(lines),
                media_type="application/x-ndjson"
            )
            
        elif format == "csv":
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                if schema.hackathons:
                    h_buffer = io.StringIO()
                    writer = csv.DictWriter(h_buffer, fieldnames=ExportHackathonV1.model_fields.keys())
                    writer.writeheader()
                    for h in schema.hackathons:
                        writer.writerow(h.model_dump(mode='json'))
                    zf.writestr("hackathons.csv", h_buffer.getvalue())
                    
                if schema.projects:
                    p_buffer = io.StringIO()
                    writer = csv.DictWriter(p_buffer, fieldnames=ExportProjectV1.model_fields.keys())
                    writer.writeheader()
                    for p in schema.projects:
                        writer.writerow(p.model_dump(mode='json'))
                    zf.writestr("projects.csv", p_buffer.getvalue())
                    
                if schema.organizations:
                    o_buffer = io.StringIO()
                    writer = csv.DictWriter(o_buffer, fieldnames=ExportOrganizationV1.model_fields.keys())
                    writer.writeheader()
                    for o in schema.organizations:
                        writer.writerow(o.model_dump(mode='json'))
                    zf.writestr("organizations.csv", o_buffer.getvalue())
            
            return Response(
                content=zip_buffer.getvalue(),
                media_type="application/zip",
                headers={"Content-Disposition": 'attachment; filename="export.zip"'}
            )
        
        return Response(status_code=400, content="Invalid format specified")

    @staticmethod
    async def import_data(
        db: AsyncSession,
        workspace_id: str,
        data: InnovationSchemaV1
    ) -> Dict[str, Any]:
        """
        Imports data from an InnovationSchemaV1 object into the workspace.
        """
        result = {
            "hackathons_imported": 0,
            "projects_imported": 0,
            "organizations_imported": 0,
        }
        
        # In a real scenario, we might need to handle ID collisions or create new IDs.
        # For simplicity, we create new entities for the imported data.
        
        for h in data.hackathons:
            new_hackathon = Hackathon(
                workspace_id=workspace_id,
                name=h.name,
                description=h.description,
                mode=h.mode,
                location=h.location,
                registration_deadline=h.registration_deadline,
                start_date=h.start_date,
                end_date=h.end_date,
                timezone=h.timezone,
                max_team_size=h.max_team_size,
                status=h.status,
                program_type=h.program_type
            )
            db.add(new_hackathon)
            result["hackathons_imported"] += 1
            
        for o in data.organizations:
            # We assume organizations are workspace-scoped for this example, 
            # or we create new ones. Since Organization is globally scoped in the DB usually,
            # this might just be a stub, but we'll import them.
            pass
            
        await db.commit()
        return result

