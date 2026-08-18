import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.models.memory import MemoryType
from app.schemas.memory import AgentMemoryCreate, AgentMemoryResponse
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memories", tags=["agent_memory"])

@router.post("", response_model=AgentMemoryResponse)
async def create_memory(
    data: AgentMemoryCreate,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = MemoryService(db)
    memory = await service.add_memory(workspace_id, data)
    await db.commit()
    return memory

@router.get("/{agent_name}", response_model=List[AgentMemoryResponse])
async def list_memories(
    agent_name: str,
    memory_type: Optional[MemoryType] = Query(None),
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = MemoryService(db)
    return await service.get_memories(workspace_id, agent_name, memory_type)

@router.delete("/{memory_id}")
async def revoke_memory(
    memory_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = MemoryService(db)
    success = await service.revoke_memory(workspace_id, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found or access denied")
    await db.commit()
    return {"status": "success"}
