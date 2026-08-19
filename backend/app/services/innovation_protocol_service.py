from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Union
import uuid
from datetime import datetime

from app.schemas.innovation_protocol import (
    InnovationObject,
    InnovationEvent,
    InnovationProject,
    InnovationChallenge,
    InnovationAchievement,
    InnovationOrganization,
    InnovationPerson,
    InnovationProgram,
    InnovationProtocolExport
)
from app.models.hackathon import Hackathon
from app.models.project import Project
from app.models.user import User
from app.models.organization import Organization

class InnovationProtocolService:
    def __init__(self, db: AsyncSession, source_system: str = "hackathon-tracker"):
        self.db = db
        self.source_system = source_system

    def _get_base_fields(self, obj: Any, obj_type: str, owner: str) -> Dict[str, Any]:
        return {
            "id": str(obj.id),
            "type": obj_type,
            "source": self.source_system,
            "owner": owner,
            "version": "1.0",
            "timestamp": getattr(obj, "updated_at", getattr(obj, "created_at", datetime.utcnow())),
            "verification": {},
            "visibility": "public",
            "relationships": {}
        }

    async def export_ecosystem(self) -> InnovationProtocolExport:
        # Fetch data
        hackathons_query = await self.db.execute(select(Hackathon))
        projects_query = await self.db.execute(select(Project))
        users_query = await self.db.execute(select(User))
        orgs_query = await self.db.execute(select(Organization))

        hackathons = hackathons_query.scalars().all()
        projects = projects_query.scalars().all()
        users = users_query.scalars().all()
        orgs = orgs_query.scalars().all()

        objects: List[InnovationObject] = []

        # Map Organizations
        for org in orgs:
            base = self._get_base_fields(org, "InnovationOrganization", owner=str(org.id))
            objects.append(InnovationOrganization(
                **base,
                name=org.name,
                domain=org.website
            ))

        # Map People
        for user in users:
            base = self._get_base_fields(user, "InnovationPerson", owner=str(user.id))
            objects.append(InnovationPerson(
                **base,
                name=user.name,
                email_hash=None, # Avoid exposing raw emails
                skills=[] # Add skills mapping if available
            ))

        # Map Events (Hackathons)
        for h in hackathons:
            owner = str(h.organization_id) if hasattr(h, "organization_id") and h.organization_id else self.source_system
            base = self._get_base_fields(h, "InnovationEvent", owner=owner)
            objects.append(InnovationEvent(
                **base,
                name=h.name,
                description=h.description,
                start_date=h.start_date,
                end_date=h.end_date,
                status=h.status
            ))

        # Map Projects
        for p in projects:
            owner = str(p.team_id) if hasattr(p, "team_id") and p.team_id else self.source_system
            base = self._get_base_fields(p, "InnovationProject", owner=owner)
            objects.append(InnovationProject(
                **base,
                title=p.title,
                summary=p.solution_summary if hasattr(p, "solution_summary") else None,
                repository_url=p.repository_url,
                status=p.status
            ))

        return InnovationProtocolExport(
            source_system=self.source_system,
            objects=objects
        )
