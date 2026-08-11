from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.federation import WorkspaceFederation, FederationStatus
from app.models.workspace import Workspace
from app.schemas.federation import WorkspaceFederationCreate, WorkspaceFederationUpdate, WorkspaceFederationResponse

class FederationService:
    @staticmethod
    async def create_federation_link(
        source_workspace_id: UUID,
        data: WorkspaceFederationCreate,
        db: AsyncSession
    ) -> WorkspaceFederationResponse:
        
        # Verify target workspace exists
        target_ws_query = select(Workspace).where(Workspace.id == data.target_workspace_id)
        result = await db.execute(target_ws_query)
        if not result.scalar_one_or_none():
            raise ValueError("Target workspace does not exist")
            
        if source_workspace_id == data.target_workspace_id:
            raise ValueError("Cannot federate with the same workspace")
            
        # Check existing link
        link_query = select(WorkspaceFederation).where(
            WorkspaceFederation.source_workspace_id == source_workspace_id,
            WorkspaceFederation.target_workspace_id == data.target_workspace_id
        )
        result = await db.execute(link_query)
        if result.scalar_one_or_none():
            raise ValueError("Federation link already exists")
            
        fed = WorkspaceFederation(
            source_workspace_id=source_workspace_id,
            target_workspace_id=data.target_workspace_id,
            status=FederationStatus.PENDING,
            shared_entities=data.shared_entities
        )
        db.add(fed)
        await db.commit()
        await db.refresh(fed)
        return WorkspaceFederationResponse.model_validate(fed)

    @staticmethod
    async def get_federation_links(
        workspace_id: UUID,
        db: AsyncSession
    ) -> List[WorkspaceFederationResponse]:
        query = select(WorkspaceFederation).where(
            or_(
                WorkspaceFederation.source_workspace_id == workspace_id,
                WorkspaceFederation.target_workspace_id == workspace_id
            )
        )
        result = await db.execute(query)
        links = result.scalars().all()
        return [WorkspaceFederationResponse.model_validate(link) for link in links]

    @staticmethod
    async def update_federation_link(
        workspace_id: UUID,
        federation_id: UUID,
        data: WorkspaceFederationUpdate,
        db: AsyncSession
    ) -> WorkspaceFederationResponse:
        query = select(WorkspaceFederation).where(WorkspaceFederation.id == federation_id)
        result = await db.execute(query)
        fed = result.scalar_one_or_none()
        if not fed:
            raise ValueError("Federation link not found")
            
        # Only target can accept/reject, either can revoke
        is_source = fed.source_workspace_id == workspace_id
        is_target = fed.target_workspace_id == workspace_id
        
        if not (is_source or is_target):
            raise ValueError("Not authorized to update this link")
            
        if data.status:
            if data.status in (FederationStatus.ACCEPTED, FederationStatus.REJECTED) and not is_target:
                raise ValueError("Only the target workspace can accept or reject a federation request")
            fed.status = data.status
            
        if data.shared_entities is not None:
            if not is_source:
                raise ValueError("Only the source workspace can update shared entities")
            fed.shared_entities = data.shared_entities
            
        await db.commit()
        await db.refresh(fed)
        return WorkspaceFederationResponse.model_validate(fed)
