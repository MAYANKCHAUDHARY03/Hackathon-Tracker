import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.submission import SubmissionRequirement, RoundSubmission, SubmissionItem
from app.models.round import HackathonRound
from app.schemas.submission import SubmissionRequirementCreate, SubmissionItemUpdate, SubmissionItemCreate
from app.models.user import User

async def get_requirements_for_round(db: AsyncSession, workspace_id: uuid.UUID, round_id: uuid.UUID) -> Sequence[SubmissionRequirement]:
    stmt = select(SubmissionRequirement).where(
        SubmissionRequirement.workspace_id == workspace_id,
        SubmissionRequirement.round_id == round_id
    ).order_by(SubmissionRequirement.sequence)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_requirement(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    req_in: SubmissionRequirementCreate,
    current_user: User
) -> SubmissionRequirement:
    
    new_req = SubmissionRequirement(
        **req_in.model_dump(),
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        round_id=round_id,
        created_by=current_user.id
    )
    db.add(new_req)
    await db.commit()
    await db.refresh(new_req)
    return new_req

async def get_team_submission(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    round_id: uuid.UUID,
    team_id: uuid.UUID
) -> RoundSubmission | None:
    stmt = select(RoundSubmission).where(
        RoundSubmission.workspace_id == workspace_id,
        RoundSubmission.round_id == round_id,
        RoundSubmission.team_id == team_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def initialize_team_submission(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    round_id: uuid.UUID,
    team_id: uuid.UUID
) -> RoundSubmission:
    existing = await get_team_submission(db, workspace_id, round_id, team_id)
    if existing:
        return existing
        
    submission = RoundSubmission(
        workspace_id=workspace_id,
        hackathon_id=hackathon_id,
        round_id=round_id,
        team_id=team_id,
        status="draft"
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission

async def update_submission_item(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    submission_id: uuid.UUID,
    item_in: SubmissionItemCreate,
    current_user: User
) -> SubmissionItem:
    
    # Verify submission exists and is not locked
    stmt = select(RoundSubmission).where(
        RoundSubmission.id == submission_id,
        RoundSubmission.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    submission = result.scalars().first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    if submission.status == "locked":
        raise HTTPException(status_code=400, detail="Submission is locked and cannot be modified")
        
    # Check if item exists
    stmt_item = select(SubmissionItem).where(
        SubmissionItem.submission_id == submission_id,
        SubmissionItem.requirement_id == item_in.requirement_id
    )
    result_item = await db.execute(stmt_item)
    item = result_item.scalars().first()
    
    # Server-side validation logic
    is_valid = True
    if item_in.content is None or len(item_in.content.strip()) == 0:
        is_valid = False
        
    # Example URL validation could go here
    if item:
        item.content = item_in.content
        item.is_valid = is_valid
        item.updated_by = current_user.id
    else:
        item = SubmissionItem(
            workspace_id=workspace_id,
            submission_id=submission_id,
            requirement_id=item_in.requirement_id,
            content=item_in.content,
            is_valid=is_valid,
            updated_by=current_user.id
        )
        db.add(item)
        
    await db.commit()
    await db.refresh(item)
    return item

async def lock_submission(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    submission_id: uuid.UUID,
    current_user: User
) -> RoundSubmission:
    stmt = select(RoundSubmission).where(
        RoundSubmission.id == submission_id,
        RoundSubmission.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    submission = result.scalars().first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    submission.status = "locked"
    submission.locked_at = datetime.now(timezone.utc)
    submission.locked_by = current_user.id
    
    # Generate snapshot of items
    items_stmt = select(SubmissionItem).where(SubmissionItem.submission_id == submission.id)
    items_result = await db.execute(items_stmt)
    items = items_result.scalars().all()
    
    snapshot_data = {}
    for item in items:
        snapshot_data[str(item.requirement_id)] = {
            "content": item.content,
            "is_valid": item.is_valid
        }
        
    submission.snapshot = snapshot_data
    
    await db.commit()
    await db.refresh(submission)
    return submission
