import uuid
import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models.memory import AgentMemory, MemoryType
from app.schemas.memory import AgentMemoryCreate

class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_memory(self, workspace_id: uuid.UUID, data: AgentMemoryCreate) -> AgentMemory:
        db_memory = AgentMemory(
            workspace_id=workspace_id,
            agent_name=data.agent_name,
            memory_type=data.memory_type,
            content=data.content,
            source_id=data.source_id,
            expires_at=data.expires_at,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        self.db.add(db_memory)
        await self.db.flush()
        return db_memory

    async def get_memories(self, workspace_id: uuid.UUID, agent_name: str, memory_type: Optional[MemoryType] = None) -> List[AgentMemory]:
        # Enforces hard organization-boundary isolation on all memory reads
        query = select(AgentMemory).where(
            and_(
                AgentMemory.workspace_id == workspace_id,
                AgentMemory.agent_name == agent_name
            )
        )
        if memory_type:
            query = query.where(AgentMemory.memory_type == memory_type)
            
        result = await self.db.execute(query)
        memories = result.scalars().all()
        
        valid_memories = [m for m in memories if not m.is_expired()]
        return valid_memories

    async def revoke_memory(self, workspace_id: uuid.UUID, memory_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(AgentMemory).where(
                and_(
                    AgentMemory.id == memory_id,
                    AgentMemory.workspace_id == workspace_id
                )
            )
        )
        memory = result.scalars().first()
        if not memory:
            return False
        
        await self.db.delete(memory)
        await self.db.flush()
        return True
