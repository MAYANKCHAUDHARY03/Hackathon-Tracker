import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.hackathon import Hackathon
from app.models.project import Project
from app.schemas.organizer_copilot import OrganizerCopilotStatus, OrganizerCopilotRecommendedAction
from app.core.agent.middleware import AgentExecutionMiddleware
from app.core.agent.registry import tool_registry
from app.schemas.agent import RiskLevel

# Register fake tools for Organizer Copilot to use via middleware
@tool_registry.register(
    name="send_mass_reminder",
    description="Sends reminder emails to teams missing demos or submissions",
    risk_level=RiskLevel.MEDIUM
)
async def send_mass_reminder(hackathon_id: str, target_group: str):
    return {"message": f"Reminders sent to {target_group} for hackathon {hackathon_id}"}

@tool_registry.register(
    name="extend_deadline",
    description="Extends the submission or evaluation deadline",
    risk_level=RiskLevel.HIGH
)
async def extend_deadline(hackathon_id: str, target_phase: str, days: int):
    return {"message": f"Deadline for {target_phase} extended by {days} days"}


class OrganizerCopilotService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def get_hackathon_status(self, hackathon_id: uuid.UUID) -> OrganizerCopilotStatus:
        result = await self.db.execute(select(Hackathon).where(Hackathon.id == hackathon_id))
        hackathon = result.scalars().first()
        if not hackathon:
            raise ValueError("Hackathon not found")

        # Mocking health stats for the Phase 52 UI demonstration
        # In a fully fleshed out data model, we would run counts grouped by statuses
        result_projects = await self.db.execute(select(Project).where(Project.hackathon_id == hackathon_id))
        projects = result_projects.scalars().all()
        
        missing_demos = len([p for p in projects if not getattr(p, "demo_url", None)])
        incomplete_submissions = 5  # Mock value
        incomplete_evaluations = 12 # Mock value
        
        risk_flags = []
        recommended_actions = []

        if missing_demos > 0:
            risk_flags.append(f"{missing_demos} projects are missing demo URLs")
            recommended_actions.append(
                OrganizerCopilotRecommendedAction(
                    action_type="send_mass_reminder",
                    description="Send reminder to teams missing demos",
                    reason=f"{missing_demos} teams haven't provided a demo URL yet.",
                    expected_impact="Should increase demo completion rate before judging starts.",
                    target_entity_id=hackathon_id,
                    target_entity_type="hackathon",
                    payload={"target_group": "missing_demos"}
                )
            )

        if incomplete_evaluations > 10:
            risk_flags.append("High volume of incomplete judge evaluations")
            recommended_actions.append(
                OrganizerCopilotRecommendedAction(
                    action_type="extend_deadline",
                    description="Extend evaluation deadline by 2 days",
                    reason="Judges are falling behind on evaluation queues.",
                    expected_impact="Reduces judge fatigue and ensures all projects get reviewed.",
                    target_entity_id=hackathon_id,
                    target_entity_type="hackathon",
                    payload={"target_phase": "evaluation", "days": 2}
                )
            )

        overall_health = "Needs Attention" if risk_flags else "Healthy"

        return OrganizerCopilotStatus(
            hackathon_id=hackathon_id,
            overall_health=overall_health,
            incomplete_submissions=incomplete_submissions,
            missing_demos=missing_demos,
            incomplete_evaluations=incomplete_evaluations,
            risk_flags=risk_flags,
            recommended_actions=recommended_actions
        )

    async def execute_action(self, hackathon_id: uuid.UUID, action: OrganizerCopilotRecommendedAction):
        middleware = AgentExecutionMiddleware(self.db, self.actor_id, self.workspace_id)
        
        agent_name = "organizer_copilot_agent"
        allowed_tools = ["send_mass_reminder", "extend_deadline"]
        
        tool_parameters = {
            "hackathon_id": str(hackathon_id)
        }
        if action.payload:
            tool_parameters.update(action.payload)
            
        return await middleware.execute_tool(
            agent_name=agent_name,
            allowed_tools=allowed_tools,
            tool_name=action.action_type,
            parameters=tool_parameters
        )
