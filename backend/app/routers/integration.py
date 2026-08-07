from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.models.integration import ExternalSubmissionConnection, ExternalSubmissionMapping
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.integration import (
    ExternalSubmissionConnectionCreate,
    ExternalSubmissionConnectionUpdate,
    ExternalSubmissionConnectionResponse,
    SyncSubmissionsRequest,
    SyncSubmissionsResponse
)
from app.services.integrations import ProviderFactory

router = APIRouter(
    prefix="/workspaces/{workspace_id}/integrations",
    tags=["integrations"]
)

@router.get("/connections", response_model=List[ExternalSubmissionConnectionResponse])
async def list_connections(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """List all external submission connections for a workspace."""
    query = select(ExternalSubmissionConnection).where(
        ExternalSubmissionConnection.workspace_id == workspace_id
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/connections", response_model=ExternalSubmissionConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    workspace_id: UUID,
    conn_in: ExternalSubmissionConnectionCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Create a new external submission connection (e.g. to Devfolio)."""
    # Verify the provider works before saving
    try:
        provider = ProviderFactory.get_provider(conn_in.provider_name, conn_in.credentials)
        is_valid = await provider.validate_credentials()
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid credentials for the specified provider")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    from app.security_vault import encrypt_dict
    
    encrypted_credentials = {"encrypted_data": encrypt_dict(conn_in.credentials)}
    
    db_conn = ExternalSubmissionConnection(
        workspace_id=workspace_id,
        provider_name=conn_in.provider_name,
        credentials=encrypted_credentials,
        is_active=conn_in.is_active
    )
    
    db.add(db_conn)
    await db.commit()
    await db.refresh(db_conn)
    return db_conn

@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    workspace_id: UUID,
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Delete an integration connection."""
    query = select(ExternalSubmissionConnection).where(
        ExternalSubmissionConnection.id == connection_id,
        ExternalSubmissionConnection.workspace_id == workspace_id
    )
    result = await db.execute(query)
    db_conn = result.scalar_one_or_none()
    
    if not db_conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    await db.delete(db_conn)
    await db.commit()
    return None

@router.post("/connections/{connection_id}/sync", response_model=SyncSubmissionsResponse)
async def sync_submissions(
    workspace_id: UUID,
    connection_id: UUID,
    sync_req: SyncSubmissionsRequest,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Sync submissions from the external provider."""
    query = select(ExternalSubmissionConnection).where(
        ExternalSubmissionConnection.id == connection_id,
        ExternalSubmissionConnection.workspace_id == workspace_id
    )
    result = await db.execute(query)
    db_conn = result.scalar_one_or_none()
    
    if not db_conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    try:
        from app.security_vault import decrypt_dict
        
        creds = db_conn.credentials
        if "encrypted_data" in creds:
            creds = decrypt_dict(creds["encrypted_data"])
            
        provider = ProviderFactory.get_provider(db_conn.provider_name, creds)
        
        # We assume the user has a specific hackathon reference id for that provider
        # that correlates to an internal hackathon.
        # For simplicity, we just trigger the fetch.
        
        submissions = await provider.sync_submissions(sync_req.hackathon_reference)
        
        # Here we would normally save mappings and round_submissions
        # For this stage, we log the success
        
        return SyncSubmissionsResponse(
            synced_count=len(submissions),
            failed_count=0,
            message="Successfully triggered sync"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
