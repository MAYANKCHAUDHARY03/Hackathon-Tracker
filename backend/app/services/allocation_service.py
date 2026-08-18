from typing import List, Dict
import uuid

from app.schemas.allocation import AllocationRequest, AllocationResponse, AllocationResult, Judge, Project

class AllocationService:
    def __init__(self):
        pass

    def allocate(self, request: AllocationRequest) -> AllocationResponse:
        allocations = []
        unallocated_projects = []

        # Sort judges by workload (ascending) so we load-balance
        judges = sorted(request.judges, key=lambda j: j.current_workload)
        
        for project in request.projects:
            assigned_judges: List[Judge] = []
            
            # 1. Expertise Match
            # 2. Conflict Check
            # 3. Availability/Workload
            
            # Score all judges for this project
            scored_judges = []
            for judge in judges:
                # Conflict Check
                if project.id in judge.conflicts:
                    continue
                
                # Workload Check
                if judge.current_workload >= judge.max_workload:
                    continue
                    
                # Expertise Score
                expertise_overlap = set(judge.expertise).intersection(set(project.domains))
                score = len(expertise_overlap)
                
                scored_judges.append((score, judge))
                
            # Sort by score (descending), then by workload (ascending)
            # Python's sort is stable, so we sort by workload first, then score
            scored_judges.sort(key=lambda x: x[1].current_workload)
            scored_judges.sort(key=lambda x: x[0], reverse=True)
            
            # Assign top N judges
            for score, judge in scored_judges:
                if len(assigned_judges) >= request.judges_per_project:
                    break
                assigned_judges.append(judge)
                judge.current_workload += 1
                
            if len(assigned_judges) < request.judges_per_project:
                unallocated_projects.append(project.id)
                
            # Generate AI-style explanation (deterministic here)
            if assigned_judges:
                reasons = []
                for j in assigned_judges:
                    overlap = set(j.expertise).intersection(set(project.domains))
                    if overlap:
                        reasons.append(f"{j.name} (Expertise: {', '.join(overlap)})")
                    else:
                        reasons.append(f"{j.name} (General Availability)")
                
                explanation = f"Allocated based on constraint engine. Matched: {'; '.join(reasons)}."
            else:
                explanation = "Failed to allocate sufficient judges due to workload and conflict constraints."

            allocations.append(AllocationResult(
                project_id=project.id,
                judge_ids=[j.id for j in assigned_judges],
                explanation=explanation
            ))

        return AllocationResponse(
            allocations=allocations,
            unallocated_projects=unallocated_projects
        )
