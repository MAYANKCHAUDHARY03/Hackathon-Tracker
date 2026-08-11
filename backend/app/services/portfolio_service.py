from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.organization import Organization
from app.schemas.portfolio import UserPortfolio, PortfolioItem, OrganizationPortfolio, OrgPortfolioStats, OrgPortfolioProject
from app.services.graph_service import KnowledgeGraphService

class PortfolioService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_portfolio(self, user_id: UUID) -> UserPortfolio:
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
            
        stmt = select(Team).join(TeamMember).where(TeamMember.user_id == user_id)
        teams = (await self.session.execute(stmt)).scalars().all()
        
        items = []
        for team in teams:
            items.append(PortfolioItem(
                id=str(team.id),
                name=team.name,
                description=team.description,
                type="team",
                url=None,
                date=team.created_at
            ))
            
        return UserPortfolio(
            user_id=str(user.id),
            full_name=user.full_name,
            bio=None,
            items=items
        )

    async def get_organization_portfolio(self, org_id: UUID, workspace_id: UUID) -> OrganizationPortfolio:
        org = await self.session.get(Organization, org_id)
        if not org:
            raise ValueError("Organization not found")

        # Traverse the graph to find all projects and startups connected to this organization
        # Org -> Hackathon/Challenge -> Project -> Startup
        graph_service = KnowledgeGraphService(self.session)
        traversal = await graph_service.traverse(start_id=org_id, workspace_id=workspace_id, depth=3)
        
        nodes = traversal.get("nodes", {})
        projects = []
        startups = []
        technologies = {}
        
        active_projects_count = 0
        completed_projects_count = 0
        
        for node_id, node_info in nodes.items():
            if node_info["type"] == "Project":
                data = node_info["data"]
                status = data.get("status", "ACTIVE")
                techs = data.get("technologies", []) or []
                
                if status == "COMPLETED" or status == "ARCHIVED":
                    completed_projects_count += 1
                else:
                    active_projects_count += 1
                    
                for tech in techs:
                    technologies[tech] = technologies.get(tech, 0) + 1
                    
                projects.append(OrgPortfolioProject(
                    id=str(data["id"]),
                    name=data["name"],
                    status=status,
                    technologies=techs,
                    description=data.get("description")
                ))
            elif node_info["type"] == "Startup":
                data = node_info["data"]
                startups.append({
                    "id": str(data["id"]),
                    "name": data["name"],
                    "description": data.get("description"),
                    "founded_date": data.get("founded_date")
                })

        # Sort technologies by frequency
        top_techs = [tech for tech, _ in sorted(technologies.items(), key=lambda x: x[1], reverse=True)[:5]]

        stats = OrgPortfolioStats(
            total_projects=len(projects),
            active_projects=active_projects_count,
            completed_projects=completed_projects_count,
            startups_spawned=len(startups),
            patents_research=0,  # Placeholder for future integration
            top_technologies=top_techs
        )

        return OrganizationPortfolio(
            org_id=str(org.id),
            name=org.name,
            stats=stats,
            projects=projects,
            startups=startups
        )
