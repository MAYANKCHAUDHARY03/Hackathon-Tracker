import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portable_project import PortableProjectIdentity, ProjectStageTransition
from app.models.portable_identity import VisibilityTier
from app.schemas.portable_project import (
    PortableProjectIdentityCreate,
    ProjectStageTransitionCreate
)

class PortableProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_portable_project(self, user_id: uuid.UUID, data: PortableProjectIdentityCreate) -> PortableProjectIdentity:
        # Check if slug exists
        stmt = select(PortableProjectIdentity).where(PortableProjectIdentity.slug == data.slug)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project slug already exists")
            
        project = PortableProjectIdentity(
            owner_id=user_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            current_stage=data.current_stage,
            visibility=data.visibility
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        # Log initial transition
        transition = ProjectStageTransition(
            portable_project_id=project.id,
            from_stage=None,
            to_stage=project.current_stage,
            notes="Initial project creation"
        )
        self.db.add(transition)
        await self.db.commit()
        
        return project

    async def get_portable_project(self, project_id: uuid.UUID, user_id: uuid.UUID) -> PortableProjectIdentity:
        project = await self.db.get(PortableProjectIdentity, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        if not self._can_view_project(project, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this project")
            
        return project

    async def record_stage_transition(
        self, 
        project_id: uuid.UUID, 
        user_id: uuid.UUID, 
        data: ProjectStageTransitionCreate
    ) -> ProjectStageTransition:
        project = await self.get_portable_project(project_id, user_id)
        
        # Only owner can record transitions for now
        if project.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can record transitions")
            
        transition = ProjectStageTransition(
            portable_project_id=project.id,
            from_stage=project.current_stage,
            to_stage=data.to_stage,
            organization_id=data.organization_id,
            program_context_id=data.program_context_id,
            program_context_type=data.program_context_type,
            notes=data.notes
        )
        
        # Update current stage on identity
        project.current_stage = data.to_stage
        
        self.db.add(transition)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(transition)
        
        return transition

    async def get_project_history(
        self, 
        project_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> tuple[PortableProjectIdentity, List[ProjectStageTransition]]:
        project = await self.get_portable_project(project_id, user_id)
        
        stmt = select(ProjectStageTransition).where(
            ProjectStageTransition.portable_project_id == project.id
        ).order_by(ProjectStageTransition.transition_date.desc())
        
        result = await self.db.execute(stmt)
        transitions = result.scalars().all()
        return project, list(transitions)
        
    def _can_view_project(self, project: PortableProjectIdentity, user_id: uuid.UUID) -> bool:
        if project.owner_id == user_id:
            return True
        if project.visibility == VisibilityTier.PUBLIC:
            return True
        # Future: Implement CONNECTION_ONLY or SELECTIVE_SHARING checks using federation trust graph
        return False

