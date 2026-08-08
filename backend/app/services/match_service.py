import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.models.team import Team
from app.models.people import Person
from app.models.user import User
from app.services.graph_service import GraphQueryService
from app.services.ai.providers import AIProviderFactory
from app.config import settings
from fastapi import HTTPException

class MatchService:
    @staticmethod
    async def evaluate_talent_matches(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID) -> List[Dict[str, Any]]:
        # 1. Fetch team
        team_stmt = select(Team).where(Team.workspace_id == workspace_id, Team.id == team_id)
        team_res = await db.execute(team_stmt)
        team = team_res.scalars().first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        skills = team.skills_needed or []
        if not skills:
            return []
            
        # 2. Use AI to extract intent/keywords from the team's needed skills
        ai_provider = AIProviderFactory.get_provider(settings.AI_PROVIDER)
        skills_str = " ".join(skills)
        intent = await ai_provider.extract_search_intent(f"Find people with skills in {skills_str}")
        
        keywords = intent.get("keywords", skills)
        
        # 3. Search Person nodes (Talent) in the workspace
        person_stmt = select(Person).where(Person.workspace_id == workspace_id, Person.archived_at.is_(None))
        person_res = await db.execute(person_stmt)
        people = person_res.scalars().all()
        
        matches = []
        for person in people:
            person_skills = person.expertise_areas or []
            
            # Simple keyword overlap scoring
            score = 0
            for skill in person_skills:
                for keyword in keywords:
                    if keyword.lower() in skill.lower() or skill.lower() in keyword.lower():
                        score += 1
            
            if score > 0:
                matches.append({
                    "person_id": str(person.id),
                    "full_name": person.full_name,
                    "designation": person.designation,
                    "expertise_areas": person_skills,
                    "match_score": score
                })
                
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

    @staticmethod
    async def apply_to_team(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID, user: User):
        # Find person associated with the user
        person_stmt = select(Person).where(Person.workspace_id == workspace_id, Person.email == user.email, Person.archived_at.is_(None))
        person_res = await db.execute(person_stmt)
        person = person_res.scalars().first()
        
        if not person:
            raise HTTPException(status_code=404, detail="User must have a Person profile to apply.")
            
        # Create GraphEdge using GraphQueryService
        graph_service = GraphQueryService(db)
        await graph_service.create_edge(
            workspace_id=workspace_id,
            source_type="Person",
            source_id=person.id,
            target_type="Team",
            target_id=team_id,
            relation_type="APPLIED_TO",
            properties={"applied_at": "now"}
        )
        return {"status": "success", "message": "Applied to team successfully."}

    @staticmethod
    async def invite_to_team(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID, person_id: uuid.UUID, user: User):
        # Create GraphEdge using GraphQueryService
        graph_service = GraphQueryService(db)
        await graph_service.create_edge(
            workspace_id=workspace_id,
            source_type="Team",
            source_id=team_id,
            target_type="Person",
            target_id=person_id,
            relation_type="INVITED_TO",
            properties={"invited_by": str(user.id)}
        )
        return {"status": "success", "message": "Invited talent to team successfully."}
