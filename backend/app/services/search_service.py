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
        results: List[SearchResultItem] = []
        
        if not query or len(query.strip()) < 2:
            return SearchResponse(query=query, results=[], total=0)
            
        search_term = f"%{query.strip()}%"
        
        # 1. Search Hackathons
        hackathons_stmt = select(Hackathon).where(
            and_(
                Hackathon.workspace_id == workspace_id,
                or_(
                    Hackathon.name.ilike(search_term),
                    Hackathon.description.ilike(search_term)
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
                metadata={"status": h.status}
            ))

        # 2. Search Projects
        projects_stmt = select(Project).where(
            and_(
                Project.workspace_id == workspace_id,
                or_(
                    Project.title.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.problem_statement.ilike(search_term)
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
                metadata={"team_id": str(p.team_id)}
            ))

        # 3. Search Teams
        teams_stmt = select(Team).where(
            and_(
                Team.workspace_id == workspace_id,
                or_(
                    Team.name.ilike(search_term),
                    Team.description.ilike(search_term)
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
                metadata={"status": t.status}
            ))

        # 4. Search Tasks
        tasks_stmt = (
            select(Task, KanbanBoard)
            .join(KanbanBoard, Task.board_id == KanbanBoard.id)
            .where(
                and_(
                    KanbanBoard.workspace_id == workspace_id,
                    or_(
                        Task.title.ilike(search_term),
                        Task.description.ilike(search_term)
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
                metadata={"priority": task.priority}
            ))
            
        # Sort results by created_at descending
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        return SearchResponse(
            query=query,
            results=results,
            total=len(results)
        )
