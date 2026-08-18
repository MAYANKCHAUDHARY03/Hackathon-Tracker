import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.program_simulation import ProgramSimulationRequest, ProgramSimulationResponse, SimulationRisk

class ProgramSimulationService:
    def __init__(self, db: AsyncSession, actor_id: uuid.UUID, workspace_id: uuid.UUID):
        self.db = db
        self.actor_id = actor_id
        self.workspace_id = workspace_id

    async def run_simulation(self, request: ProgramSimulationRequest) -> ProgramSimulationResponse:
        # Expected load
        submissions_per_team = request.rounds_count
        total_submissions = request.team_count * submissions_per_team
        
        # Judge Requirements
        # Assume each submission needs 3 evaluations, and a judge can do 10 evaluations per day
        total_evaluations = total_submissions * 3
        # Simplification: assuming evaluations happen evenly over duration
        evals_per_day = total_evaluations / max(1, request.duration_days)
        ideal_judges = math.ceil(evals_per_day / 10.0)
        
        # Mentor Requirements
        # 1 mentor per 8 teams
        ideal_mentors = math.ceil(request.team_count / 8.0)
        
        # Infra Requirements
        concurrent_users = math.ceil(request.participant_count * 0.7) # 70% peak concurrency
        api_requests_per_sec = math.ceil(concurrent_users * 0.05) # 0.05 RPS per user
        
        risks = []
        is_viable = True
        
        if request.judges_available < ideal_judges:
            shortfall = ideal_judges - request.judges_available
            risks.append(SimulationRisk(
                risk_factor="Judge Shortage",
                severity="HIGH" if shortfall > ideal_judges * 0.5 else "MEDIUM",
                mitigation=f"Recruit {shortfall} more judges or reduce evaluations per submission."
            ))
            if shortfall > ideal_judges * 0.5:
                is_viable = False
                
        if request.mentors_available < ideal_mentors:
            risks.append(SimulationRisk(
                risk_factor="Mentor Shortage",
                severity="MEDIUM",
                mitigation=f"Recruit {ideal_mentors - request.mentors_available} more mentors to ensure quality support."
            ))
            
        if request.duration_days < request.rounds_count * 2:
            risks.append(SimulationRisk(
                risk_factor="Schedule Compression",
                severity="HIGH",
                mitigation="Increase duration or reduce rounds to avoid participant burnout."
            ))
            is_viable = False
            
        if not risks:
            risks.append(SimulationRisk(
                risk_factor="None",
                severity="LOW",
                mitigation="Program is well-resourced."
            ))

        return ProgramSimulationResponse(
            expected_load={
                "total_submissions": total_submissions,
                "total_evaluations": total_evaluations,
                "peak_concurrent_users": concurrent_users
            },
            judge_requirements={
                "ideal_count": ideal_judges,
                "available_count": request.judges_available,
                "status": "SUFFICIENT" if request.judges_available >= ideal_judges else "DEFICIENT"
            },
            mentor_requirements={
                "ideal_count": ideal_mentors,
                "available_count": request.mentors_available,
                "status": "SUFFICIENT" if request.mentors_available >= ideal_mentors else "DEFICIENT"
            },
            infrastructure_requirements={
                "peak_rps": api_requests_per_sec,
                "recommended_tier": "Standard" if api_requests_per_sec < 100 else "Premium"
            },
            projected_risks=risks,
            is_viable=is_viable
        )
