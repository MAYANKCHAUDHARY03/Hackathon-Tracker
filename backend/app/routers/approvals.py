import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.approval import AgentApprovalRequest, ApprovalStatus
from app.schemas.agent import AgentApprovalRequestResponse
from app.core.agent.registry import tool_registry

# For demonstration, we use a fixed user and workspace UUID
DUMMY_USER_ID = uuid.uuid4()
DUMMY_WORKSPACE_ID = uuid.uuid4()

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("", response_model=List[AgentApprovalRequestResponse])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    """
    List all pending agent tool approvals.
    """
    result = await db.execute(
        select(AgentApprovalRequest).where(AgentApprovalRequest.status == ApprovalStatus.PENDING)
    )
    approvals = result.scalars().all()
    
    # We must explicitly convert the SQL objects to Pydantic objects or dictionaries 
    # to avoid nested async SQLAlchemy issues in some serialization cases.
    response = []
    for app in approvals:
        response.append(AgentApprovalRequestResponse(
            id=str(app.id),
            workspace_id=str(app.workspace_id),
            agent_name=app.agent_name,
            tool_name=app.tool_name,
            parameters_json=app.parameters_json,
            risk_level=app.risk_level,
            status=app.status.value,
            requested_at=app.requested_at,
            justification=app.justification,
            resolved_by_id=str(app.resolved_by_id) if app.resolved_by_id else None,
            resolved_at=app.resolved_at
        ))
    return response

@router.post("/{approval_id}/approve")
async def approve_request(approval_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Approve a pending request and execute the tool.
    """
    result = await db.execute(
        select(AgentApprovalRequest).where(AgentApprovalRequest.id == approval_id)
    )
    approval_request = result.scalars().first()
    
    if not approval_request:
        raise HTTPException(status_code=404, detail="Approval request not found")
        
    if approval_request.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Request is already {approval_request.status.value}")
        
    # Mark as approved
    approval_request.status = ApprovalStatus.APPROVED
    approval_request.resolved_by_id = DUMMY_USER_ID
    
    import datetime
    approval_request.resolved_at = datetime.datetime.utcnow()
    
    # Execute the tool
    handler = tool_registry.get_handler(approval_request.tool_name)
    if not handler:
        raise HTTPException(status_code=500, detail="Tool handler not found in registry")
        
    try:
        execution_result = await handler(**approval_request.parameters_json)
        status = "success"
        error = None
    except Exception as e:
        execution_result = None
        status = "error"
        error = str(e)
        
    # Emit to EventService
    from app.services.event_service import EventService
    from app.schemas.event import EventCreate, EventType
    
    event_service = EventService(db)
    event_create = EventCreate(
        workspace_id=approval_request.workspace_id,
        actor_id=DUMMY_USER_ID,
        entity_type="Agent",
        entity_id=approval_request.agent_name,
        event_type=EventType.GENERAL_ACTIVITY,
        source="agent_framework",
        metadata_json={
            "tool_name": approval_request.tool_name,
            "parameters": approval_request.parameters_json,
            "status": status,
            "error": error,
            "human_approved": True,
            "approval_id": str(approval_request.id)
        }
    )
    await event_service.publish(event_create)
    
    await db.commit()
    
    return {
        "status": status,
        "result": execution_result,
        "error": error
    }

@router.post("/{approval_id}/reject")
async def reject_request(approval_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Reject a pending request.
    """
    result = await db.execute(
        select(AgentApprovalRequest).where(AgentApprovalRequest.id == approval_id)
    )
    approval_request = result.scalars().first()
    
    if not approval_request:
        raise HTTPException(status_code=404, detail="Approval request not found")
        
    if approval_request.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Request is already {approval_request.status.value}")
        
    approval_request.status = ApprovalStatus.REJECTED
    approval_request.resolved_by_id = DUMMY_USER_ID
    
    import datetime
    approval_request.resolved_at = datetime.datetime.utcnow()
    
    await db.commit()
    return {"status": "rejected"}
