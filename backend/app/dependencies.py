from fastapi import Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.config import settings
from app.models.user import User, WorkspaceMembership

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_uuid, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user

async def verify_workspace_access(
    workspace_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceMembership:
    stmt = select(WorkspaceMembership).where(
        WorkspaceMembership.workspace_id == workspace_id,
        WorkspaceMembership.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied"
        )
    return membership

async def require_workspace_admin(
    membership: WorkspaceMembership = Depends(verify_workspace_access)
) -> WorkspaceMembership:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Must be owner or admin."
        )
    return membership


async def verify_team_access(
    team_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.team import TeamMember
    stmt = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or access denied"
        )
    return membership

async def require_team_lead_or_colead(
    membership = Depends(verify_team_access)
):
    if membership.authorization_role not in {"lead", "co_lead"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient team permissions. Must be lead or co-lead."
        )
    return membership

async def require_team_lead(
    membership = Depends(verify_team_access)
):
    if membership.authorization_role != "lead":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient team permissions. Must be lead."
        )
    return membership


async def verify_organization_access(
    organization_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.organization import OrganizationMembership
    from app.models.organization_trust import OrganizationTrust, TrustStatus
    from app.models.federated_identity import FederatedIdentity, FederationStatus
    
    # 1. Direct Membership Check
    stmt = select(OrganizationMembership).where(
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.status == "active"
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if membership:
        return {"type": "direct", "membership": membership}

    # 2. Check existing active Federated Identity
    fed_stmt = select(FederatedIdentity).where(
        FederatedIdentity.user_id == current_user.id,
        FederatedIdentity.target_org_id == organization_id,
        FederatedIdentity.status == FederationStatus.ACTIVE
    )
    fed_result = await db.execute(fed_stmt)
    fed_identity = fed_result.scalar_one_or_none()
    
    if fed_identity:
        return {"type": "federated", "identity": fed_identity}

    # 3. Cross-Org / Federated Trust Check (Attempt to establish)
    user_orgs_stmt = select(OrganizationMembership.organization_id).where(
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.status == "active"
    )
    user_orgs_result = await db.execute(user_orgs_stmt)
    user_org_ids = [row[0] for row in user_orgs_result.all()]
    
    if not user_org_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or access denied"
        )
        
    trust_stmt = select(OrganizationTrust).where(
        OrganizationTrust.trustor_org_id == organization_id,
        OrganizationTrust.trustee_org_id.in_(user_org_ids),
        OrganizationTrust.status == TrustStatus.ACTIVE
    )
    trust_result = await db.execute(trust_stmt)
    trust = trust_result.scalars().first()
    
    if trust:
        # Implicitly establish the identity for this session
        from app.services.organization_federation_service import OrganizationFederationService
        new_fed_identity = await OrganizationFederationService.establish_federated_identity(
            db=db,
            user_id=current_user.id,
            home_org_id=trust.trustee_org_id,
            target_org_id=organization_id
        )
        return {"type": "federated", "identity": new_fed_identity}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Organization not found or access denied"
    )
