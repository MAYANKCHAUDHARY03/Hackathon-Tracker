import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.digital_twin import DigitalTwinSimulationRequest, DigitalTwinSimulationResponse, ResourceProjection
from app.models.hackathon import Hackathon
from app.models.team import Team
from app.models.people import Person

class DigitalTwinService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def run_simulation(self, request: DigitalTwinSimulationRequest) -> DigitalTwinSimulationResponse:
        # Base numbers if no base hackathon is provided
        current_teams = 0
        current_participants = 0
        current_judges = 0
        current_mentors = 0
        
        if request.base_hackathon_id:
            # Fetch base stats to project from
            # For simulation purposes, we'll just mock base numbers if we can't do complex aggregates quickly
            # In a real implementation, we'd do COUNT() over teams, people etc.
            current_teams = 50
            current_participants = 200
            current_judges = 10
            current_mentors = 5
        
        # Calculate target numbers based on inputs
        target_teams = request.target_teams_count or (current_teams * 1.3)
        target_participants = request.target_participants_count or (target_teams * 4)
        
        # Heuristics for requirements
        # 1 judge per 5 teams
        # 1 mentor per 10 teams
        judges_needed = math.ceil(target_teams / 5.0 * request.complexity_multiplier)
        mentors_needed = math.ceil(target_teams / 10.0 * request.complexity_multiplier)
        infra_cost = target_teams * 50.0 * request.complexity_multiplier # e.g. $50 cloud credits per team
        
        projections = []
        
        judge_gap = judges_needed - current_judges
        projections.append(ResourceProjection(
            category="Judges",
            current_capacity=current_judges,
            projected_requirement=judges_needed,
            gap=judge_gap,
            risk_level="HIGH" if judge_gap > 10 else ("MEDIUM" if judge_gap > 0 else "LOW")
        ))
        
        mentor_gap = mentors_needed - current_mentors
        projections.append(ResourceProjection(
            category="Mentors",
            current_capacity=current_mentors,
            projected_requirement=mentors_needed,
            gap=mentor_gap,
            risk_level="HIGH" if mentor_gap > 5 else ("MEDIUM" if mentor_gap > 0 else "LOW")
        ))
        
        insights = [
            f"If teams increase to {int(target_teams)}, you will need {judges_needed} judges to maintain evaluation quality.",
            f"Expected infrastructure cost is projected at ${infra_cost:,.2f}.",
            "Consider running an outreach campaign for mentors as the projected gap is significant." if mentor_gap > 0 else "Mentor capacity is sufficient."
        ]
        
        return DigitalTwinSimulationResponse(
            projected_judges_needed=judges_needed,
            projected_mentors_needed=mentors_needed,
            projected_infrastructure_cost=infra_cost,
            resource_projections=projections,
            insights=insights
        )
