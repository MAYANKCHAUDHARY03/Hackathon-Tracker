from uuid import UUID
from typing import List, Any
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hackathon import Hackathon
from app.models.project import Project
from app.models.team import Team
from app.models.kanban import Task, KanbanBoard
from app.schemas.search import SearchResultItem, SearchResponse

class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(self, workspace_id: UUID, query: str) -> SearchResponse:
        from app.services.ai.providers import AIProviderFactory
        from app.services.graph_service import KnowledgeGraphService
        from app.config import settings
        
        results: List[SearchResultItem] = []
        
        if not query or len(query.strip()) < 2:
            return SearchResponse(query=query, results=[], total=0)
            
        # 1. AI Intent Extraction
        ai_provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY)
        intent = await ai_provider.extract_search_intent(query)
        entities_to_search = intent.get("entities", ["project", "hackathon", "team", "task"])
        keywords = intent.get("keywords", [query.strip()])
        
        # Build search condition
        if not keywords:
            keywords = [query.strip()]
            
        # Simple OR over all keywords for ILIKE
        search_terms = [f"%{k}%" for k in keywords]
        
        def build_or_condition(column):
            return or_(*[column.ilike(t) for t in search_terms])
            
        # 2. Search Base Entities
        if "hackathon" in entities_to_search:
            hackathons_stmt = select(Hackathon).where(
                and_(
                    Hackathon.workspace_id == workspace_id,
                    or_(
                        build_or_condition(Hackathon.name),
                        build_or_condition(Hackathon.description)
                    )
                )
            ).limit(10)
            
            hackathons = (await self.session.execute(hackathons_stmt)).scalars().all()
            for h in hackathons:
                results.append(SearchResultItem(
                    id=h.id,
                    type="hackathon",
                    title=h.name,
                    description=h.description[:100] + "..." if h.description and len(h.description) > 100 else h.description,
                    url=f"/workspaces/{workspace_id}/hackathons/{h.id}",
                    created_at=h.created_at,
                    edge_edge_metadata={"status": h.status}
                ))

        if "project" in entities_to_search:
            projects_stmt = select(Project).where(
                and_(
                    Project.workspace_id == workspace_id,
                    or_(
                        build_or_condition(Project.title),
                        build_or_condition(Project.description),
                        build_or_condition(Project.problem_statement)
                    )
                )
            ).limit(10)
            
            projects = (await self.session.execute(projects_stmt)).scalars().all()
            for p in projects:
                results.append(SearchResultItem(
                    id=p.id,
                    type="project",
                    title=p.title,
                    description=p.description[:100] + "..." if p.description and len(p.description) > 100 else p.description,
                    url=f"/workspaces/{workspace_id}/projects/{p.id}",
                    created_at=p.created_at,
                    edge_edge_metadata={"team_id": str(p.team_id)}
                ))

        if "team" in entities_to_search:
            teams_stmt = select(Team).where(
                and_(
                    Team.workspace_id == workspace_id,
                    or_(
                        build_or_condition(Team.name),
                        build_or_condition(Team.description)
                    )
                )
            ).limit(10)
            
            teams = (await self.session.execute(teams_stmt)).scalars().all()
            for t in teams:
                results.append(SearchResultItem(
                    id=t.id,
                    type="team",
                    title=t.name,
                    description=t.description[:100] + "..." if t.description and len(t.description) > 100 else t.description,
                    url=f"/workspaces/{workspace_id}/teams/{t.id}",
                    created_at=t.created_at,
                    edge_edge_metadata={"status": t.status}
                ))

        if "task" in entities_to_search:
            tasks_stmt = (
                select(Task, KanbanBoard)
                .join(KanbanBoard, Task.board_id == KanbanBoard.id)
                .where(
                    and_(
                        KanbanBoard.workspace_id == workspace_id,
                        or_(
                            build_or_condition(Task.title),
                            build_or_condition(Task.description)
                        )
                    )
                )
                .limit(10)
            )
            
            tasks_result = (await self.session.execute(tasks_stmt)).all()
            for task, board in tasks_result:
                results.append(SearchResultItem(
                    id=task.id,
                    type="task",
                    title=task.title,
                    description=task.description[:100] + "..." if task.description and len(task.description) > 100 else task.description,
                    url=f"/workspaces/{workspace_id}/projects/{board.project_id}/kanban?task={task.id}",
                    created_at=task.created_at,
                    edge_edge_metadata={"priority": task.priority}
                ))
                
        # Sort results by created_at descending
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # 3. Graph Context Hydration (Phase 19 integration)
        graph_service = KnowledgeGraphService(self.session)
        for result in results[:15]:
            try:
                graph_data = await graph_service.traverse(start_id=result.id, workspace_id=workspace_id, depth=1)
                
                context = {}
                for node_id, node_info in graph_data.get("nodes", {}).items():
                    if str(node_id) == str(result.id):
                        continue
                    node_type = node_info.get("type")
                    if node_type not in context:
                        context[node_type] = []
                    
                    data = node_info.get("data", {})
                    name = data.get("title") or data.get("name") or data.get("first_name") or "Unknown"
                    context[node_type].append(name)
                
                result.graph_context = context
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to fetch graph context for {result.id}: {e}")
        
        return SearchResponse(
            query=query,
            results=results,
            total=len(results)
        )
