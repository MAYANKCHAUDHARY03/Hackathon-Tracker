from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta


def _ensure_utc_aware(dt: datetime) -> datetime:
    """Ensure a datetime is UTC-aware (SQLite may strip tzinfo on retrieval)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

from app.database import get_db
from app.models.user import User, WorkspaceMembership
from app.models.workspace_invitation import WorkspaceInvitation
from app.schemas.workspace import WorkspaceInvitationCreate, WorkspaceInvitationResponse
from app.dependencies import get_current_user, verify_workspace_access, require_workspace_admin

router = APIRouter()

@router.post("/workspaces/{workspace_id}/invitations", response_model=WorkspaceInvitationResponse)
async def invite_user(
    invitation: WorkspaceInvitationCreate,
    workspace_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    # Check if user is already a member
    stmt = select(User).join(WorkspaceMembership).where(
        User.email == invitation.email,
        WorkspaceMembership.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace"
        )

    # Check if there's already a pending invitation
    stmt = select(WorkspaceInvitation).where(
        WorkspaceInvitation.workspace_id == workspace_id,
        WorkspaceInvitation.email == invitation.email,
        WorkspaceInvitation.status == "pending"
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already sent to this email"
        )

    token = str(uuid4())

    new_invitation = WorkspaceInvitation(
        workspace_id=workspace_id,
        email=invitation.email,
        workspace_role=invitation.role,
        invited_by=current_user.id,
        token_hash=token, # In a real app this would be hashed
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    db.add(new_invitation)
    await db.commit()
    await db.refresh(new_invitation)
    
    return new_invitation

@router.get("/workspaces/{workspace_id}/invitations", response_model=list[WorkspaceInvitationResponse])
async def list_invitations(
    workspace_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    stmt = select(WorkspaceInvitation).where(
        WorkspaceInvitation.workspace_id == workspace_id,
        WorkspaceInvitation.status == "pending"
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.delete("/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invitation(
    invitation_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation_id)
    result = await db.execute(stmt)
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    # Only workspace admin or the invited user (if they have an account matching the email) can revoke/decline
    if invitation.email != current_user.email:
        # Check if admin
        admin_stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == invitation.workspace_id,
            WorkspaceMembership.user_id == current_user.id,
            WorkspaceMembership.role.in_(["owner", "admin"])
        )
        admin_result = await db.execute(admin_stmt)
        if not admin_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized to revoke this invitation")
    
    await db.delete(invitation)
    await db.commit()

@router.post("/invitations/{token}/accept")
async def accept_invitation(
    token: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(WorkspaceInvitation).where(
        WorkspaceInvitation.token_hash == token,
        WorkspaceInvitation.status == "pending"
    )
    result = await db.execute(stmt)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation")
    
    if _ensure_utc_aware(invitation.expires_at) < datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(status_code=400, detail="Invitation has expired")

    if invitation.email != current_user.email:
        raise HTTPException(status_code=400, detail="This invitation is for a different email address")

    # Create workspace membership
    new_membership = WorkspaceMembership(
        workspace_id=invitation.workspace_id,
        user_id=current_user.id,
        role=invitation.workspace_role
    )
    db.add(new_membership)

    invitation.status = "accepted"
    invitation.accepted_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"status": "accepted", "workspace_id": invitation.workspace_id}
