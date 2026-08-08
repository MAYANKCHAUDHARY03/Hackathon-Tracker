import uuid
from typing import List
import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, verify_workspace_access
from app.models.user import User, WorkspaceMembership
from app.schemas.people import (
    PersonCreate, PersonUpdate, PersonResponse, 
    MentorAssignmentCreate, MentorAssignmentUpdate, MentorAssignmentResponse,
    CsvImportResult
)
from app.services import people_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}",
    tags=["mentors"]
)

@router.get("/people", response_model=List[PersonResponse])
async def list_people(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await people_service.get_people(db, workspace_id)

@router.post("/people", response_model=PersonResponse)
async def create_person(
    workspace_id: uuid.UUID,
    person_in: PersonCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await people_service.create_person(db, workspace_id, current_user.id, person_in)

@router.get("/hackathons/{hackathon_id}/mentors", response_model=List[MentorAssignmentResponse])
async def list_mentors(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await people_service.get_mentor_assignments(db, workspace_id, hackathon_id)

@router.post("/hackathons/{hackathon_id}/mentors", response_model=MentorAssignmentResponse)
async def create_mentor(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    assignment_in: MentorAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    assignment_in.hackathon_id = hackathon_id
    return await people_service.create_mentor_assignment(db, workspace_id, current_user.id, assignment_in)

@router.post("/hackathons/{hackathon_id}/people/import", response_model=CsvImportResult)
async def import_people_csv(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    contents = await file.read()
    try:
        decoded = contents.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            decoded = contents.decode('utf-8')
        except:
            raise HTTPException(status_code=400, detail="Invalid file encoding. Please upload a UTF-8 encoded CSV.")

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or invalid")
    
    # Normalize headers
    normalized_fieldnames = [f.strip().lower().replace(" ", "_") for f in reader.fieldnames]
    reader.fieldnames = normalized_fieldnames
    
    rows = list(reader)
    
    return await people_service.import_people_csv(
        db, workspace_id, hackathon_id, current_user.id, rows
    )
