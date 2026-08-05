import uuid
from typing import List
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.submission import (
    SubmissionRequirementCreate, 
    SubmissionRequirementResponse, 
    RoundSubmissionResponse,
    SubmissionItemCreate,
    SubmissionItemResponse
)
from app.services.submission_service import (
    get_requirements_for_round,
    create_requirement,
    initialize_team_submission,
    update_submission_item,
    lock_submission,
    get_team_submission
)

router = APIRouter(prefix="/hackathons/{hackathon_id}/rounds/{round_id}", tags=["Submissions"])

@router.get("/requirements", response_model=List[SubmissionRequirementResponse])
async def read_requirements(
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_requirements_for_round(db, x_workspace_id, round_id)

@router.post("/requirements", response_model=SubmissionRequirementResponse)
async def add_requirement(
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    req_in: SubmissionRequirementCreate,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_requirement(db, x_workspace_id, hackathon_id, round_id, req_in, current_user)

@router.get("/teams/{team_id}/submission", response_model=RoundSubmissionResponse)
async def get_or_create_submission(
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    team_id: uuid.UUID,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = await initialize_team_submission(db, x_workspace_id, hackathon_id, round_id, team_id)
    # the relationship 'items' is used in the response model, ensure it's loaded if we need to.
    # The default lazy load on async might fail without proper selectinload.
    # To keep it simple, we can fetch items and populate them manually or update the service query.
    return submission

@router.post("/teams/{team_id}/submission/items", response_model=SubmissionItemResponse)
async def update_item(
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    team_id: uuid.UUID,
    item_in: SubmissionItemCreate,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = await get_team_submission(db, x_workspace_id, round_id, team_id)
    if not submission:
        submission = await initialize_team_submission(db, x_workspace_id, hackathon_id, round_id, team_id)
        
    return await update_submission_item(db, x_workspace_id, submission.id, item_in, current_user)

@router.post("/teams/{team_id}/submission/lock", response_model=RoundSubmissionResponse)
async def lock_team_submission(
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    team_id: uuid.UUID,
    x_workspace_id: uuid.UUID = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = await get_team_submission(db, x_workspace_id, round_id, team_id)
    if not submission:
        submission = await initialize_team_submission(db, x_workspace_id, hackathon_id, round_id, team_id)
        
    return await lock_submission(db, x_workspace_id, submission.id, current_user)
