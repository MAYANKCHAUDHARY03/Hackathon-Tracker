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
