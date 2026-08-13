import uuid
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.ontology import UniversalEntity, EntityType
from app.schemas.ontology import UniversalEntityCreate, UniversalEntityUpdate

class OntologyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_entity(
        self, 
        workspace_id: uuid.UUID, 
        entity_type: EntityType,
        data: UniversalEntityCreate
    ) -> UniversalEntity:
        if data.entity_type != entity_type:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Path entity type {entity_type} does not match payload {data.entity_type}"
            )
             
        entity = UniversalEntity(
            workspace_id=workspace_id,
            entity_type=data.entity_type,
            owner_id=data.owner_id,
            source=data.source,
            verification_level=data.verification_level,
            visibility=data.visibility,
            properties=data.properties
        )
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_entity(
        self, 
        workspace_id: uuid.UUID, 
        entity_type: EntityType,
        entity_id: uuid.UUID
    ) -> UniversalEntity:
        stmt = select(UniversalEntity).where(
            and_(
                UniversalEntity.workspace_id == workspace_id,
                UniversalEntity.entity_type == entity_type,
                UniversalEntity.id == entity_id
            )
        )
        result = await self.session.execute(stmt)
        entity = result.scalars().first()
        
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_type.value} not found")
            
        return entity

    async def list_entities(
        self, 
        workspace_id: uuid.UUID, 
        entity_type: EntityType,
        limit: int = 50,
        offset: int = 0
    ) -> List[UniversalEntity]:
        stmt = select(UniversalEntity).where(
            and_(
                UniversalEntity.workspace_id == workspace_id,
                UniversalEntity.entity_type == entity_type
            )
        ).order_by(UniversalEntity.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_entity(
        self, 
        workspace_id: uuid.UUID, 
        entity_type: EntityType,
        entity_id: uuid.UUID,
        data: UniversalEntityUpdate
    ) -> UniversalEntity:
        entity = await self.get_entity(workspace_id, entity_type, entity_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)
            
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
