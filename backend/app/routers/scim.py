from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, List
import hashlib
from passlib.context import CryptContext

from app.database import get_db
from app.models.scim_token import ScimToken
from app.models.user import User
from app.models.organization import OrganizationMembership

router = APIRouter()

async def verify_scim_token(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> ScimToken:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
        
    token = authorization.split(" ")[1]
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    stmt = select(ScimToken).where(ScimToken.token_hash == token_hash)
    scim_token = (await db.execute(stmt)).scalar_one_or_none()
    
    if not scim_token:
        raise HTTPException(status_code=401, detail="Invalid SCIM token")
        
    return scim_token

def user_to_scim_resource(user: User) -> Dict[str, Any]:
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": str(user.id),
        "userName": user.email,
        "name": {
            "formatted": user.full_name
        },
        "emails": [
            {
                "value": user.email,
                "primary": True
            }
        ],
        "active": user.is_active
    }

@router.get("/Users")
async def get_users(scim_token: ScimToken = Depends(verify_scim_token), db: AsyncSession = Depends(get_db)):
    # Simple list of users in org (SCIM filtering not fully implemented in MVP, but framework is here)
    stmt = select(User).join(OrganizationMembership).where(OrganizationMembership.organization_id == scim_token.organization_id)
    users = (await db.execute(stmt)).scalars().all()
    
    resources = [user_to_scim_resource(u) for u in users]
    
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(resources),
        "itemsPerPage": len(resources),
        "startIndex": 1,
        "Resources": resources
    }

@router.post("/Users", status_code=201)
async def create_user(request: Request, scim_token: ScimToken = Depends(verify_scim_token), db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    email = payload.get("userName")
    
    # Check if user exists
    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    
    if existing:
        user = existing
    else:
        name = payload.get("name", {}).get("formatted", email)
        user = User(
            full_name=name,
            email=email,
            password_hash="!scim_provisioned",
            is_active=payload.get("active", True)
        )
        db.add(user)
        await db.flush()

    # Ensure organization membership
    org_stmt = select(OrganizationMembership).where(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.organization_id == scim_token.organization_id
    )
    org_member = (await db.execute(org_stmt)).scalar_one_or_none()
    
    if not org_member:
        new_membership = OrganizationMembership(
            user_id=user.id,
            organization_id=scim_token.organization_id,
            role="member"
        )
        db.add(new_membership)

    await db.commit()
    
    return user_to_scim_resource(user)

@router.get("/Users/{user_id}")
async def get_user(user_id: str, scim_token: ScimToken = Depends(verify_scim_token), db: AsyncSession = Depends(get_db)):
    stmt = select(User).join(OrganizationMembership).where(
        User.id == user_id,
        OrganizationMembership.organization_id == scim_token.organization_id
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user_to_scim_resource(user)

@router.put("/Users/{user_id}")
async def update_user(user_id: str, request: Request, scim_token: ScimToken = Depends(verify_scim_token), db: AsyncSession = Depends(get_db)):
    stmt = select(User).join(OrganizationMembership).where(
        User.id == user_id,
        OrganizationMembership.organization_id == scim_token.organization_id
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    payload = await request.json()
    
    if "active" in payload:
        user.is_active = payload["active"]
    if "name" in payload and "formatted" in payload["name"]:
        user.full_name = payload["name"]["formatted"]
        
    await db.commit()
    return user_to_scim_resource(user)
