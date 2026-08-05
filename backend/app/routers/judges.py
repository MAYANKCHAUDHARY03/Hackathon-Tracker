import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, verify_workspace_access
from app.models.user import User, WorkspaceMembership
from app.schemas.people import JudgeAssignmentCreate, JudgeAssignmentUpdate, JudgeAssignmentResponse
from app.services import people_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}/hackathons/{hackathon_id}/judges",
    tags=["judges"]
)

@router.get("/", response_model=List[JudgeAssignmentResponse])
async def list_judges(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await people_service.get_judge_assignments(db, workspace_id, hackathon_id)

@router.post("/", response_model=JudgeAssignmentResponse)
async def create_judge(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    assignment_in: JudgeAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    assignment_in.hackathon_id = hackathon_id
    return await people_service.create_judge_assignment(db, workspace_id, current_user.id, assignment_in)
