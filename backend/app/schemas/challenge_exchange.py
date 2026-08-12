import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ProblemSchema(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class ChallengeSchema(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    hackathon_id: Optional[uuid.UUID] = None
    problem_id: Optional[uuid.UUID] = None
    title: str
    slug: str
    description: Optional[str] = None
    category: Optional[str] = None
    domain: Optional[str] = None
    difficulty: Optional[str] = None
    visibility: str
    submission_count: int
    status: str
    created_at: datetime
    problem: Optional[ProblemSchema] = None

    class Config:
        from_attributes = True

class ProblemListResponse(BaseModel):
    problems: List[ProblemSchema]

class ChallengeListResponse(BaseModel):
    challenges: List[ChallengeSchema]
