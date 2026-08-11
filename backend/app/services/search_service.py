import math
import uuid
import logging
from typing import List, Any, Dict
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hackathon import Hackathon
from app.models.project import Project
from app.models.team import Team
from app.models.kanban import Task, KanbanBoard
from app.models.search import ContentEmbedding
from app.schemas.search import SearchResultItem, SearchResponse
from app.services.ai.providers import AIProviderFactory
from app.config import settings

logger = logging.getLogger(__name__)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = sum(a * a for a in v1) ** 0.5
    norm_b = sum(b * b for b in v2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def index_entity(self, workspace_id: uuid.UUID, entity_type: str, entity_id: uuid.UUID, text_content: str):
        """Generates and stores an embedding for the entity."""
        ai_provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY)
        embedding_vector = await ai_provider.generate_embedding(text_content)
        
        # Calculate a simple hash to track changes
        import hashlib
        content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
        
        stmt = select(ContentEmbedding).where(
            ContentEmbedding.workspace_id == workspace_id,
            ContentEmbedding.entity_type == entity_type,
            ContentEmbedding.entity_id == entity_id
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        
        if existing:
            if existing.content_hash == content_hash:
                return # No change
            existing.embedding = embedding_vector
            existing.content_hash = content_hash
            existing.model_version = "text-embedding-004" if isinstance(ai_provider, AIProviderFactory.get_provider("gemini", "").__class__) else "mock-001"
        else:
            new_emb = ContentEmbedding(
                workspace_id=workspace_id,
                entity_type=entity_type,
                entity_id=entity_id,
                embedding=embedding_vector,
                content_hash=content_hash,
                model_version="text-embedding-004" if isinstance(ai_provider, AIProviderFactory.get_provider("gemini", "").__class__) else "mock-001"
            )
            self.session.add(new_emb)
            
        await self.session.commit()

    async def search(self, workspace_id: uuid.UUID, query: str) -> SearchResponse:
        from app.services.graph_service import KnowledgeGraphService
        
        results_dict: Dict[uuid.UUID, SearchResultItem] = {}
        
        if not query or len(query.strip()) < 2:
            return SearchResponse(query=query, results=[], total=0)
            
        ai_provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY)
        
        # 1. AI Intent Extraction
        intent = await ai_provider.extract_search_intent(query)
        entities_to_search = intent.get("entities", ["project", "hackathon", "team", "task"])
        keywords = intent.get("keywords", [query.strip()])
        
        if not keywords:
            keywords = [query.strip()]
            
        # 2. Semantic Search (Mocking pgvector with in-memory cosine similarity for now)
        query_embedding = await ai_provider.generate_embedding(query)
        
        # Load all embeddings for the workspace (feasible for small-medium workspaces, pgvector needed for scale)
        emb_stmt = select(ContentEmbedding).where(ContentEmbedding.workspace_id == workspace_id)
        embeddings = (await self.session.execute(emb_stmt)).scalars().all()
        
        vector_scores = {}
        for emb in embeddings:
            if emb.entity_type.lower() in entities_to_search:
                sim = cosine_similarity(query_embedding, emb.embedding)
                if sim > 0.6: # Semantic threshold
                    vector_scores[emb.entity_id] = sim

        # 3. Keyword Search (Base Entities)
        search_terms = [f"%{k}%" for k in keywords]
        def build_or_condition(column):
            return or_(*[column.ilike(t) for t in search_terms])
            
        # Fetch entities that either matched vector search OR keyword search
        
        if "hackathon" in entities_to_search:
            vector_ids = [k for k, v in vector_scores.items() if v > 0] # Filter by type could be done here if vector_scores tracked type
            hackathons_stmt = select(Hackathon).where(
                and_(
                    Hackathon.workspace_id == workspace_id,
                    or_(
                        build_or_condition(Hackathon.name),
                        build_or_condition(Hackathon.description),
                        Hackathon.id.in_(vector_ids) if vector_ids else False
                    )
                )
            ).limit(20)
            
            hackathons = (await self.session.execute(hackathons_stmt)).scalars().all()
            for h in hackathons:
                score = vector_scores.get(h.id, 0.0)
                # Boost if matched keywords as well
                if any(k.lower() in h.name.lower() or (h.description and k.lower() in h.description.lower()) for k in keywords):
                    score += 0.5
                results_dict[h.id] = SearchResultItem(
                    id=h.id, type="hackathon", title=h.name,
                    description=h.description[:100] + "..." if h.description and len(h.description) > 100 else h.description,
                    url=f"/workspaces/{workspace_id}/hackathons/{h.id}",
                    created_at=h.created_at,
                    edge_edge_metadata={"status": h.status, "score": score}
                )

        if "project" in entities_to_search:
            vector_ids = [k for k, v in vector_scores.items() if v > 0]
            projects_stmt = select(Project).where(
                and_(
                    Project.workspace_id == workspace_id,
                    or_(
                        build_or_condition(Project.title),
                        build_or_condition(Project.description),
                        build_or_condition(Project.problem_statement),
                        Project.id.in_(vector_ids) if vector_ids else False
                    )
                )
            ).limit(20)
            
            projects = (await self.session.execute(projects_stmt)).scalars().all()
            for p in projects:
                score = vector_scores.get(p.id, 0.0)
                if any(k.lower() in p.title.lower() or (p.description and k.lower() in p.description.lower()) for k in keywords):
                    score += 0.5
                results_dict[p.id] = SearchResultItem(
                    id=p.id, type="project", title=p.title,
                    description=p.description[:100] + "..." if p.description and len(p.description) > 100 else p.description,
                    url=f"/workspaces/{workspace_id}/projects/{p.id}",
                    created_at=p.created_at,
                    edge_edge_metadata={"team_id": str(p.team_id), "score": score}
                )

        if "team" in entities_to_search:
            vector_ids = [k for k, v in vector_scores.items() if v > 0]
            teams_stmt = select(Team).where(
                and_(
                    Team.workspace_id == workspace_id,
                    or_(
                        build_or_condition(Team.name),
                        build_or_condition(Team.description),
                        Team.id.in_(vector_ids) if vector_ids else False
                    )
                )
            ).limit(20)
            
            teams = (await self.session.execute(teams_stmt)).scalars().all()
            for t in teams:
                score = vector_scores.get(t.id, 0.0)
                if any(k.lower() in t.name.lower() or (t.description and k.lower() in t.description.lower()) for k in keywords):
                    score += 0.5
                results_dict[t.id] = SearchResultItem(
                    id=t.id, type="team", title=t.name,
                    description=t.description[:100] + "..." if t.description and len(t.description) > 100 else t.description,
                    url=f"/workspaces/{workspace_id}/teams/{t.id}",
                    created_at=t.created_at,
                    edge_edge_metadata={"status": t.status, "score": score}
                )

        if "task" in entities_to_search:
            vector_ids = [k for k, v in vector_scores.items() if v > 0]
            tasks_stmt = (
                select(Task, KanbanBoard)
                .join(KanbanBoard, Task.board_id == KanbanBoard.id)
                .where(
                    and_(
                        KanbanBoard.workspace_id == workspace_id,
                        or_(
                            build_or_condition(Task.title),
                            build_or_condition(Task.description),
                            Task.id.in_(vector_ids) if vector_ids else False
                        )
                    )
                )
                .limit(20)
            )
            
            tasks_result = (await self.session.execute(tasks_stmt)).all()
            for task, board in tasks_result:
                score = vector_scores.get(task.id, 0.0)
                if any(k.lower() in task.title.lower() or (task.description and k.lower() in task.description.lower()) for k in keywords):
                    score += 0.5
                results_dict[task.id] = SearchResultItem(
                    id=task.id, type="task", title=task.title,
                    description=task.description[:100] + "..." if task.description and len(task.description) > 100 else task.description,
                    url=f"/workspaces/{workspace_id}/projects/{board.project_id}/kanban?task={task.id}",
                    created_at=task.created_at,
                    edge_edge_metadata={"priority": task.priority, "score": score}
                )
                
        # 4. Sort results by hybrid score (descending)
        results = list(results_dict.values())
        results.sort(key=lambda x: x.edge_edge_metadata.get("score", 0.0), reverse=True)
        results = results[:20] # Keep top 20
        
        # 5. Graph Context Hydration
        graph_service = KnowledgeGraphService(self.session)
        for result in results[:10]: # Only hydrate context for top 10 to save time
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
                logger.warning(f"Failed to fetch graph context for {result.id}: {e}")
        
        return SearchResponse(
            query=query,
            results=results,
            total=len(results)
        )
