from uuid import UUID
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.project import Project
from app.models.team import Team
from app.models.hackathon import Hackathon
from app.models.graph import GraphEdge
from app.schemas.copilot import CopilotQuery, CopilotResponse, SourceEntity
from app.services.ai import AIProviderFactory
from app.config import settings

class CopilotService:
    @staticmethod
    async def ask_copilot(
        workspace_id: UUID, 
        user_id: UUID, 
        query: CopilotQuery, 
        db: AsyncSession
    ) -> CopilotResponse:
        
        # 1. Initialize AI Provider
        if settings.GEMINI_API_KEY:
            provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY)
        else:
            provider = AIProviderFactory.get_provider("mock", "dummy_key")

        # 2. Intent Detection
        intent = await provider.extract_search_intent(query.query)
        keywords = intent.get("keywords", [])
        
        # 3. Knowledge Graph/Search & Permission Check (Implicit by workspace_id filtering)
        # For simplicity, we search Projects and Teams in this workspace matching keywords
        context_lines = []
        source_entities = []
        
        # We can simulate the trusted graph search by fetching Projects
        if keywords:
            search_filters = [Project.title.ilike(f"%{kw}%") for kw in keywords]
            search_filters.extend([Project.description.ilike(f"%{kw}%") for kw in keywords])
            
            project_query = select(Project).where(
                Project.workspace_id == workspace_id,
                or_(*search_filters)
            ).limit(5)
            
            project_result = await db.execute(project_query)
            projects = project_result.scalars().all()
            
            for p in projects:
                context_lines.append(f"Project '{p.name}': {p.description}")
                source_entities.append(SourceEntity(id=p.id, type="project", name=p.name))
        
        # Fallback if no context found
        if not context_lines:
            context_lines.append("No specific data found for these keywords in the current workspace.")
            
        context_str = "\n".join(context_lines)
        
        # 4. AI Reasoning -> Answer + Evidence
        ai_result = await provider.generate_copilot_response(query.query, context_str)
        
        return CopilotResponse(
            answer=ai_result.get("answer", "No answer could be generated."),
            evidence=ai_result.get("evidence", []),
            source_entities=source_entities,
            confidence=ai_result.get("confidence", 0.0),
            recommended_action=ai_result.get("recommended_action")
        )
