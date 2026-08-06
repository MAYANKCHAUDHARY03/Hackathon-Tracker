from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.hackathon import Hackathon
from app.models.round import HackathonRound
from app.models.submission import SubmissionRequirement
from app.schemas.hackathon_export import HackathonExport, HackathonRoundExport, HackathonRequirementExport, HackathonImportRequest

router = APIRouter()

@router.get("/{hackathon_id}/export", response_model=HackathonExport)
async def export_hackathon(hackathon_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Hackathon).where(Hackathon.id == hackathon_id)
    hackathon = (await db.execute(stmt)).scalar_one_or_none()
    
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
        
    # Get Rounds
    rounds_stmt = select(HackathonRound).where(HackathonRound.hackathon_id == hackathon.id)
    rounds = (await db.execute(rounds_stmt)).scalars().all()
    
    # Get Requirements
    reqs_stmt = select(SubmissionRequirement).where(SubmissionRequirement.hackathon_id == hackathon.id)
    reqs = (await db.execute(reqs_stmt)).scalars().all()

    export_data = HackathonExport(
        title=hackathon.title,
        description=hackathon.description,
        start_date=hackathon.start_date,
        end_date=hackathon.end_date,
        timezone=hackathon.timezone,
        theme=hackathon.theme,
        rounds=[
            HackathonRoundExport(
                name=r.name,
                description=r.description,
                start_time=r.start_time,
                end_time=r.end_time
            ) for r in rounds
        ],
        requirements=[
            HackathonRequirementExport(
                title=r.title,
                description=r.description,
                is_required=r.is_required
            ) for r in reqs
        ]
    )
    
    return export_data

@router.post("/import", status_code=201)
async def import_hackathon(request: HackathonImportRequest, db: AsyncSession = Depends(get_db)):
    # 1. Create Hackathon
    hackathon = Hackathon(
        workspace_id=request.workspace_id,
        title=request.data.title,
        description=request.data.description,
        start_date=request.data.start_date,
        end_date=request.data.end_date,
        timezone=request.data.timezone,
        theme=request.data.theme,
        status="draft", # default status for imported
        created_by="system_import"
    )
    db.add(hackathon)
    await db.flush()
    
    # 2. Add Rounds
    for rnd in request.data.rounds:
        new_round = HackathonRound(
            workspace_id=request.workspace_id,
            hackathon_id=hackathon.id,
            name=rnd.name,
            description=rnd.description,
            start_time=rnd.start_time,
            end_time=rnd.end_time,
            status="pending"
        )
        db.add(new_round)
        
    # 3. Add Requirements
    for req in request.data.requirements:
        new_req = SubmissionRequirement(
            workspace_id=request.workspace_id,
            hackathon_id=hackathon.id,
            title=req.title,
            description=req.description,
            is_required=req.is_required,
            created_by="system_import"
        )
        db.add(new_req)
        
    await db.commit()
    
    return {"status": "success", "hackathon_id": str(hackathon.id)}
