from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
import uuid

from app.database import get_db
from app.models.application import ApplicationForm, ApplicationSubmission
from app.models.hackathon import Hackathon
from app.schemas.application import (
    ApplicationForm as ApplicationFormSchema,
    ApplicationFormCreate,
    ApplicationFormUpdate,
    ApplicationSubmission as ApplicationSubmissionSchema,
    ApplicationSubmissionCreate,
    ApplicationSubmissionUpdateStatus
)

router = APIRouter()

# --- FORMS ---

@router.post("/hackathons/{hackathon_id}/forms", response_model=ApplicationFormSchema)
async def create_form(hackathon_id: str, form_in: ApplicationFormCreate, db: AsyncSession = Depends(get_db)):
    # Verify hackathon exists
    result = await db.execute(select(Hackathon).filter(Hackathon.id == hackathon_id))
    hackathon = result.scalar_one_or_none()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
        
    db_form = ApplicationForm(
        id=str(uuid.uuid4()),
        hackathon_id=hackathon_id,
        title=form_in.title,
        description=form_in.description,
        schema_json=form_in.schema_json,
        is_published=form_in.is_published
    )
    db.add(db_form)
    await db.commit()
    await db.refresh(db_form)
    return db_form

@router.get("/hackathons/{hackathon_id}/forms", response_model=List[ApplicationFormSchema])
async def list_forms(hackathon_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationForm).filter(ApplicationForm.hackathon_id == hackathon_id))
    forms = result.scalars().all()
    return forms

@router.get("/forms/{form_id}", response_model=ApplicationFormSchema)
async def get_form(form_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationForm).filter(ApplicationForm.id == form_id))
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form

# --- SUBMISSIONS ---

@router.post("/forms/{form_id}/submissions", response_model=ApplicationSubmissionSchema)
async def create_submission(form_id: str, submission_in: ApplicationSubmissionCreate, db: AsyncSession = Depends(get_db)):
    # Verify form exists
    result = await db.execute(select(ApplicationForm).filter(ApplicationForm.id == form_id))
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
        
    db_submission = ApplicationSubmission(
        id=str(uuid.uuid4()),
        form_id=form_id,
        # user_id can be added here if authenticated user context is provided, for now we leave it None or get it from context
        data_json=submission_in.data_json,
        status="pending"
    )
    db.add(db_submission)
    await db.commit()
    await db.refresh(db_submission)
    return db_submission

@router.get("/hackathons/{hackathon_id}/submissions", response_model=List[ApplicationSubmissionSchema])
async def list_submissions(hackathon_id: str, db: AsyncSession = Depends(get_db)):
    # Get all forms for the hackathon
    forms_result = await db.execute(select(ApplicationForm).filter(ApplicationForm.hackathon_id == hackathon_id))
    forms = forms_result.scalars().all()
    form_ids = [f.id for f in forms]
    
    if not form_ids:
        return []
        
    submissions_result = await db.execute(
        select(ApplicationSubmission).filter(ApplicationSubmission.form_id.in_(form_ids))
    )
    submissions = submissions_result.scalars().all()
    return submissions

@router.patch("/submissions/{submission_id}/status", response_model=ApplicationSubmissionSchema)
async def update_submission_status(submission_id: str, status_update: ApplicationSubmissionUpdateStatus, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationSubmission).filter(ApplicationSubmission.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    if status_update.status not in ["pending", "approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    submission.status = status_update.status
    await db.commit()
    await db.refresh(submission)
    return submission
