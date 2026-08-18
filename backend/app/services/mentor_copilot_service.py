import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.project import Project
from app.schemas.mentor_copilot import MentorCopilotBrief, MentorRecommendedResource

class MentorCopilotService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def generate_brief(self, project_id: uuid.UUID) -> MentorCopilotBrief:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise ValueError("Project not found")

        # Mocking mentor brief for Phase 53
        # In a real scenario, this would aggregate commit history, agent memory logs, etc.
        return MentorCopilotBrief(
            project_id=project_id,
            team_name="Team Alpha", # Mock team name
            project_title=project.name,
            progress_summary="The team has completed the initial setup and database schema but is struggling with the frontend integration.",
            recent_activity=[
                "Added 3 new API endpoints for user auth",
                "Updated database schema to include user roles",
                "Struggled with React Context API setup for the last 2 days"
            ],
            flagged_blockers=[
                "State management in React (Context API vs Redux)",
                "CORS issues when calling the backend from the frontend"
            ],
            suggested_agenda=[
                "Review frontend state management approach",
                "Debug CORS configuration together",
                "Set goals for the next 48 hours"
            ],
            recommended_resources=[
                MentorRecommendedResource(
                    title="React Context vs Redux",
                    url="https://reactjs.org/docs/context.html",
                    reason="To help the team decide on a state management solution."
                ),
                MentorRecommendedResource(
                    title="FastAPI CORS Setup",
                    url="https://fastapi.tiangolo.com/tutorial/cors/",
                    reason="To resolve the current API connection blockers."
                )
            ]
        )
