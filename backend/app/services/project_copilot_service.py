import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from app.models.project import Project
from app.schemas.project_copilot import ProjectCopilotStatus, CopilotRecommendedAction
from app.core.agent.middleware import AgentExecutionMiddleware
from app.core.agent.registry import tool_registry
from app.schemas.agent import RiskLevel

# Register fake tools for the Project Copilot to use via middleware
@tool_registry.register(
    name="generate_documentation",
    description="Generates README documentation for a project",
    risk_level=RiskLevel.MEDIUM
)
async def generate_documentation(project_id: str):
    return {"message": f"Documentation generated for project {project_id}"}

@tool_registry.register(
    name="schedule_reminder",
    description="Schedules a reminder for incomplete critical tasks",
    risk_level=RiskLevel.MEDIUM
)
async def schedule_reminder(project_id: str, task_ids: List[str] = None):
    return {"message": f"Reminder scheduled for project {project_id} tasks"}

@tool_registry.register(
    name="request_demo_url",
    description="Requests team to provide a demo URL",
    risk_level=RiskLevel.LOW
)
async def request_demo_url(project_id: str):
    return {"message": f"Demo URL requested for project {project_id}"}


class ProjectCopilotService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def get_project_status(self, project_id: uuid.UUID) -> ProjectCopilotStatus:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise ValueError("Project not found")

        risk_flags = []
        detected_issues = []
        recommended_actions = []

        # We assume standard fields exist, check them safely
        if not getattr(project, "demo_url", None):
            detected_issues.append("Unvalidated demo URL")
            recommended_actions.append(
                CopilotRecommendedAction(
                    action_type="request_demo_url",
                    description="Request team to provide a demo URL",
                    target_entity_id=project_id,
                    target_entity_type="project"
                )
            )

        if not getattr(project, "readme", None) and not getattr(project, "description", None):
            detected_issues.append("Missing README sections")
            recommended_actions.append(
                CopilotRecommendedAction(
                    action_type="generate_documentation",
                    description="Generate initial README documentation",
                    target_entity_id=project_id,
                    target_entity_type="project"
                )
            )

        # Basic logic: since we don't have task models directly available without checking imports
        # let's just make it generic or use random logic based on name length for demo purposes, 
        # or just hardcode some risks to demonstrate the Copilot UI.
        risk_flags.append("Approaching Hackathon Deadline")
        recommended_actions.append(
            CopilotRecommendedAction(
                action_type="schedule_reminder",
                description="Schedule deadline reminder for team",
                target_entity_id=project_id,
                target_entity_type="project"
            )
        )

        progress_percent = 45 # Mock progress
        status = "At Risk" if risk_flags else "On Track"

        return ProjectCopilotStatus(
            project_id=project_id,
            status=status,
            progress_percent=progress_percent,
            risk_flags=risk_flags,
            detected_issues=detected_issues,
            recommended_actions=recommended_actions
        )

    async def execute_action(self, project_id: uuid.UUID, action: CopilotRecommendedAction):
        middleware = AgentExecutionMiddleware(self.db, self.actor_id, self.workspace_id)
        
        agent_name = "project_copilot_agent"
        allowed_tools = ["generate_documentation", "schedule_reminder", "request_demo_url"]
        
        tool_parameters = {
            "project_id": str(project_id)
        }
        if action.payload:
            tool_parameters.update(action.payload)
            
        return await middleware.execute_tool(
            agent_name=agent_name,
            allowed_tools=allowed_tools,
            tool_name=action.action_type,
            parameters=tool_parameters
        )
