import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.models.ontology import EntityType
from app.schemas.ontology import UniversalEntityCreate, UniversalEntityUpdate, UniversalEntityResponse
from app.services.ontology_service import OntologyService

router = APIRouter(prefix="/ontology", tags=["ontology"])

@router.post("/{entity_type}", response_model=UniversalEntityResponse)
async def create_entity(
    entity_type: EntityType,
    data: UniversalEntityCreate,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = OntologyService(db)
    return await service.create_entity(
        workspace_id=workspace_id,
        entity_type=entity_type,
        data=data
    )

@router.get("/{entity_type}", response_model=List[UniversalEntityResponse])
async def list_entities(
    entity_type: EntityType,
    workspace_id: uuid.UUID = Query(...),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = OntologyService(db)
    return await service.list_entities(
        workspace_id=workspace_id,
        entity_type=entity_type,
        limit=limit,
        offset=offset
    )

@router.get("/{entity_type}/{entity_id}", response_model=UniversalEntityResponse)
async def get_entity(
    entity_type: EntityType,
    entity_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = OntologyService(db)
    return await service.get_entity(
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id
    )

@router.put("/{entity_type}/{entity_id}", response_model=UniversalEntityResponse)
async def update_entity(
    entity_type: EntityType,
    entity_id: uuid.UUID,
    data: UniversalEntityUpdate,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    service = OntologyService(db)
    return await service.update_entity(
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id,
        data=data
    )
