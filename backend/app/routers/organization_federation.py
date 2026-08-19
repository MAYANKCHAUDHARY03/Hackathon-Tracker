from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, verify_organization_access
from app.models.organization_trust import OrganizationTrust, TrustStatus

router = APIRouter(prefix="/organizations/{organization_id}/federation", tags=["Organization Federation"])

class TrustProposal(BaseModel):
    trustee_org_id: UUID
    allowed_scopes: List[str]

class TrustResponse(BaseModel):
    id: UUID
    trustor_org_id: UUID
    trustee_org_id: UUID
    status: TrustStatus
    allowed_scopes: List[str]

    class Config:
        orm_mode = True

@router.get("/trusts", response_model=List[TrustResponse])
async def list_trusts(
    organization_id: UUID,
    access_info: dict = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    if access_info["type"] != "direct":
        raise HTTPException(status_code=403, detail="Must be a direct member to view trusts")
    
    stmt = select(OrganizationTrust).where(
        (OrganizationTrust.trustor_org_id == organization_id) | 
        (OrganizationTrust.trustee_org_id == organization_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/trusts", response_model=TrustResponse)
async def propose_trust(
    organization_id: UUID,
    proposal: TrustProposal,
    access_info: dict = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    if access_info["type"] != "direct":
        raise HTTPException(status_code=403, detail="Must be a direct member to propose trust")
    
    if organization_id == proposal.trustee_org_id:
        raise HTTPException(status_code=400, detail="Cannot trust self")
        
    stmt = select(OrganizationTrust).where(
        OrganizationTrust.trustor_org_id == organization_id,
        OrganizationTrust.trustee_org_id == proposal.trustee_org_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Trust relationship already exists")
        
    trust = OrganizationTrust(
        trustor_org_id=organization_id,
        trustee_org_id=proposal.trustee_org_id,
        status=TrustStatus.PENDING,
        allowed_scopes=proposal.allowed_scopes
    )
    db.add(trust)
    await db.commit()
    await db.refresh(trust)
    return trust

@router.post("/trusts/{trust_id}/accept", response_model=TrustResponse)
async def accept_trust(
    organization_id: UUID,
    trust_id: UUID = Path(...),
    access_info: dict = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    if access_info["type"] != "direct":
        raise HTTPException(status_code=403, detail="Must be a direct member to manage trust")
        
    stmt = select(OrganizationTrust).where(OrganizationTrust.id == trust_id)
    result = await db.execute(stmt)
    trust = result.scalar_one_or_none()
    
    if not trust:
        raise HTTPException(status_code=404, detail="Trust not found")
        
    if trust.trustee_org_id != organization_id:
        raise HTTPException(status_code=403, detail="Only trustee can accept a trust proposal")
        
    trust.status = TrustStatus.ACTIVE
    await db.commit()
    await db.refresh(trust)
    return trust

@router.delete("/trusts/{trust_id}", status_code=204)
async def revoke_trust(
    organization_id: UUID,
    trust_id: UUID = Path(...),
    access_info: dict = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    if access_info["type"] != "direct":
        raise HTTPException(status_code=403, detail="Must be a direct member to revoke trust")
        
    stmt = select(OrganizationTrust).where(OrganizationTrust.id == trust_id)
    result = await db.execute(stmt)
    trust = result.scalar_one_or_none()
    
    if not trust:
        raise HTTPException(status_code=404, detail="Trust not found")
        
    if trust.trustor_org_id != organization_id and trust.trustee_org_id != organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to revoke this trust")
        
    await db.delete(trust)
    await db.commit()
    return None
