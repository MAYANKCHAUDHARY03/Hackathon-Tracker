import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project, Technology
from app.models.organization import Organization
from app.models.sponsor import Sponsor
from app.models.user import User
from app.models.graph import GraphEdge
from app.schemas.marketplace import MarketplaceProjectItem, MarketplacePartnerItem

class MarketplaceService:
    @staticmethod
    async def get_projects_seeking_partners(db: AsyncSession, workspace_id: uuid.UUID) -> List[MarketplaceProjectItem]:
        # Fetch projects that are in INCUBATION or PILOT phase
        stmt = select(Project).where(
            Project.workspace_id == workspace_id,
            Project.status.in_(["INCUBATION", "PILOT"])
        )
        result = await db.execute(stmt)
        projects = result.scalars().all()
        
        # Hydrate technologies and origins from the graph
        edge_stmt = select(GraphEdge).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.source_type == "Project"
        )
        edges = (await db.execute(edge_stmt)).scalars().all()

        marketplace_projects = []
        for p in projects:
            p_edges = [e for e in edges if e.source_id == p.id]
            
            technologies = []
            hackathon_origin = None
            
            for e in p_edges:
                if e.target_type == "Technology" and e.relation_type == "uses":
                    # We could fetch the technology name from DB, but for now we'll just try to lookup or use ID
                    technologies.append(str(e.target_id))
            
            # Find hackathon origin (Hackathon -> contains -> Project)
            in_edges_stmt = select(GraphEdge).where(
                GraphEdge.workspace_id == workspace_id,
                GraphEdge.target_id == p.id,
                GraphEdge.source_type == "Hackathon"
            )
            in_edges = (await db.execute(in_edges_stmt)).scalars().all()
            if in_edges:
                hackathon_origin = str(in_edges[0].source_id)
            
            item = MarketplaceProjectItem(
                id=p.id,
                title=p.title,
                slug=p.slug,
                status=p.status,
                description=p.description,
                technologies=technologies,
                hackathon_origin=hackathon_origin
            )
            marketplace_projects.append(item)
            
        return marketplace_projects

    @staticmethod
    async def get_partners_seeking_projects(db: AsyncSession, workspace_id: uuid.UUID) -> List[MarketplacePartnerItem]:
        # For partners, we can look at Organizations, Sponsors, or Users with specific tags or roles
        # In this implementation, we will list all external organizations and sponsors available in the workspace.
        
        partners = []
        
        org_stmt = select(Organization).where(Organization.ecosystem_opt_in == True)
        orgs = (await db.execute(org_stmt)).scalars().all()
        
        for org in orgs:
            partners.append(MarketplacePartnerItem(
                id=org.id,
                type="Organization",
                name=org.name,
                description=None,
                resources_offered=["Funding", "Mentorship", "Pilots"] # Simulated resources
            ))
            
        sponsor_stmt = select(Sponsor).where(Sponsor.workspace_id == workspace_id)
        sponsors = (await db.execute(sponsor_stmt)).scalars().all()
        
        for sponsor in sponsors:
            partners.append(MarketplacePartnerItem(
                id=sponsor.id,
                type="Sponsor",
                name=sponsor.name,
                description=sponsor.description,
                resources_offered=["Funding", "API Credits"]
            ))
            
        return partners
