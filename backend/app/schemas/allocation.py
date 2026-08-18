from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

class Judge(BaseModel):
    id: uuid.UUID
    name: str
    expertise: List[str]
    conflicts: List[uuid.UUID]  # Project IDs they cannot judge
    max_workload: int
    current_workload: int = 0

class Project(BaseModel):
    id: uuid.UUID
    name: str
    domains: List[str]

class AllocationResult(BaseModel):
    project_id: uuid.UUID
    judge_ids: List[uuid.UUID]
    explanation: str

class AllocationRequest(BaseModel):
    judges: List[Judge]
    projects: List[Project]
    judges_per_project: int = 3

class AllocationResponse(BaseModel):
    allocations: List[AllocationResult]
    unallocated_projects: List[uuid.UUID]
