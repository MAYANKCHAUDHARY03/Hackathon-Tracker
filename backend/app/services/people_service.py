import uuid
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.people import Person, MentorAssignment, JudgeAssignment
from app.schemas.people import PersonCreate, PersonUpdate, MentorAssignmentCreate, MentorAssignmentUpdate, JudgeAssignmentCreate, JudgeAssignmentUpdate
from sqlalchemy.orm import selectinload

async def get_people(db: AsyncSession, workspace_id: uuid.UUID) -> Sequence[Person]:
    query = select(Person).where(Person.workspace_id == workspace_id, Person.archived_at.is_(None))
    result = await db.execute(query)
    return result.scalars().all()

async def get_person(db: AsyncSession, workspace_id: uuid.UUID, person_id: uuid.UUID) -> Person:
    query = select(Person).where(Person.workspace_id == workspace_id, Person.id == person_id, Person.archived_at.is_(None))
    result = await db.execute(query)
    person = result.scalars().first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

async def create_person(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: PersonCreate) -> Person:
    person = Person(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(person)
    await db.commit()
    await db.refresh(person)
    return person

async def update_person(db: AsyncSession, workspace_id: uuid.UUID, person_id: uuid.UUID, user_id: uuid.UUID, data: PersonUpdate) -> Person:
    person = await get_person(db, workspace_id, person_id)
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(person, key, value)
        
    person.updated_by = user_id
    await db.commit()
    await db.refresh(person)
    return person

async def get_mentor_assignments(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[MentorAssignment]:
    query = select(MentorAssignment).options(selectinload(MentorAssignment.mentor)).where(
        MentorAssignment.workspace_id == workspace_id, 
        MentorAssignment.hackathon_id == hackathon_id,
        MentorAssignment.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def create_mentor_assignment(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: MentorAssignmentCreate) -> MentorAssignment:
    assignment = MentorAssignment(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    # Refresh to load relations
    return await get_mentor_assignment(db, workspace_id, assignment.id)

async def get_mentor_assignment(db: AsyncSession, workspace_id: uuid.UUID, assignment_id: uuid.UUID) -> MentorAssignment:
    query = select(MentorAssignment).options(selectinload(MentorAssignment.mentor)).where(
        MentorAssignment.workspace_id == workspace_id, 
        MentorAssignment.id == assignment_id
    )
    result = await db.execute(query)
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Mentor assignment not found")
    return assignment

async def get_judge_assignments(db: AsyncSession, workspace_id: uuid.UUID, hackathon_id: uuid.UUID) -> Sequence[JudgeAssignment]:
    query = select(JudgeAssignment).options(selectinload(JudgeAssignment.judge)).where(
        JudgeAssignment.workspace_id == workspace_id, 
        JudgeAssignment.hackathon_id == hackathon_id,
        JudgeAssignment.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def create_judge_assignment(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID, data: JudgeAssignmentCreate) -> JudgeAssignment:
    assignment = JudgeAssignment(
        workspace_id=workspace_id,
        created_by=user_id,
        updated_by=user_id,
        **data.model_dump()
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return await get_judge_assignment(db, workspace_id, assignment.id)

async def get_judge_assignment(db: AsyncSession, workspace_id: uuid.UUID, assignment_id: uuid.UUID) -> JudgeAssignment:
    query = select(JudgeAssignment).options(selectinload(JudgeAssignment.judge)).where(
        JudgeAssignment.workspace_id == workspace_id, 
        JudgeAssignment.id == assignment_id
    )
    result = await db.execute(query)
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Judge assignment not found")
    return assignment

async def get_person_by_email(db: AsyncSession, workspace_id: uuid.UUID, email: str) -> Person | None:
    query = select(Person).where(
        Person.workspace_id == workspace_id,
        Person.email == email,
        Person.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def import_people_csv(
    db: AsyncSession, 
    workspace_id: uuid.UUID, 
    hackathon_id: uuid.UUID, 
    user_id: uuid.UUID, 
    rows: list[dict]
) -> dict:
    total = len(rows)
    successful = 0
    errors = []

    for idx, row in enumerate(rows, start=1):
        try:
            email = row.get("email", "").strip()
            full_name = row.get("full_name", "").strip()
            role = row.get("role", "").strip().lower()

            if not email or not full_name:
                errors.append(f"Row {idx}: missing email or full_name")
                continue

            if role not in ["mentor", "judge"]:
                errors.append(f"Row {idx}: role must be 'mentor' or 'judge', got '{role}'")
                continue

            # Find existing person
            person = await get_person_by_email(db, workspace_id, email)
            if not person:
                person = Person(
                    workspace_id=workspace_id,
                    created_by=user_id,
                    updated_by=user_id,
                    full_name=full_name,
                    email=email,
                    organisation=row.get("organisation", "").strip(),
                    designation=row.get("designation", "").strip(),
                    expertise_areas=[x.strip() for x in row.get("expertise_areas", "").split(",") if x.strip()] if row.get("expertise_areas") else []
                )
                db.add(person)
                await db.flush()  # to get person.id

            if role == "mentor":
                # Check if assignment already exists
                q_mentor = select(MentorAssignment).where(
                    MentorAssignment.workspace_id == workspace_id,
                    MentorAssignment.hackathon_id == hackathon_id,
                    MentorAssignment.mentor_id == person.id
                )
                existing = await db.execute(q_mentor)
                if not existing.scalars().first():
                    assignment = MentorAssignment(
                        workspace_id=workspace_id,
                        hackathon_id=hackathon_id,
                        mentor_id=person.id,
                        created_by=user_id,
                        updated_by=user_id
                    )
                    db.add(assignment)
            elif role == "judge":
                q_judge = select(JudgeAssignment).where(
                    JudgeAssignment.workspace_id == workspace_id,
                    JudgeAssignment.hackathon_id == hackathon_id,
                    JudgeAssignment.judge_id == person.id
                )
                existing = await db.execute(q_judge)
                if not existing.scalars().first():
                    assignment = JudgeAssignment(
                        workspace_id=workspace_id,
                        hackathon_id=hackathon_id,
                        judge_id=person.id,
                        created_by=user_id,
                        updated_by=user_id
                    )
                    db.add(assignment)

            successful += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")

    await db.commit()
    return {
        "total_processed": total,
        "successful": successful,
        "failed": len(errors),
        "errors": errors
    }
