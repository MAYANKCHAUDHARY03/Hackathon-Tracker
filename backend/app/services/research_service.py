import uuid
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.research import ResearchLink
from app.models.project import Project
from app.schemas.research import ResearchLinkCreate, ResearchLinkUpdate

class ResearchService:
    @staticmethod
    async def create_link(
        db: AsyncSession, 
        workspace_id: uuid.UUID, 
        user_id: uuid.UUID, 
        data: ResearchLinkCreate
    ) -> ResearchLink:
        # Verify project exists in workspace
        project = await db.scalar(
            select(Project)
            .where(Project.id == data.project_id)
            .where(Project.workspace_id == workspace_id)
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        link = ResearchLink(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            project_id=data.project_id,
            type=data.type,
            title=data.title,
            url=data.url,
            identifier=data.identifier,
            authors=data.authors,
            publication_date=data.publication_date,
            provenance="user-provided",
            created_by=user_id,
            updated_by=user_id
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    @staticmethod
    async def get_links_for_project(
        db: AsyncSession,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID
    ) -> List[ResearchLink]:
        result = await db.execute(
            select(ResearchLink)
            .where(ResearchLink.workspace_id == workspace_id)
            .where(ResearchLink.project_id == project_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_link(
        db: AsyncSession,
        workspace_id: uuid.UUID,
        link_id: uuid.UUID,
        user_id: uuid.UUID,
        data: ResearchLinkUpdate
    ) -> ResearchLink:
        link = await db.scalar(
            select(ResearchLink)
            .where(ResearchLink.id == link_id)
            .where(ResearchLink.workspace_id == workspace_id)
        )
        if not link:
            raise HTTPException(status_code=404, detail="Research link not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(link, key, value)
            
        link.updated_by = user_id
        await db.commit()
        await db.refresh(link)
        return link

    @staticmethod
    async def delete_link(
        db: AsyncSession,
        workspace_id: uuid.UUID,
        link_id: uuid.UUID
    ) -> None:
        link = await db.scalar(
            select(ResearchLink)
            .where(ResearchLink.id == link_id)
            .where(ResearchLink.workspace_id == workspace_id)
        )
        if not link:
            raise HTTPException(status_code=404, detail="Research link not found")
            
        await db.delete(link)
        await db.commit()
