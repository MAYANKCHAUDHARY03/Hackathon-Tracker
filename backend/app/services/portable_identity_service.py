from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.portable_identity import PortableIdentity, VerifiedSkill
from app.schemas.portable_identity import PortableIdentityUpdate, PortableIdentityResponse, VerifiedSkillSchema

class PortableIdentityService:
    @staticmethod
    async def get_or_create_identity(user_id: UUID, db: AsyncSession) -> PortableIdentityResponse:
        query = select(PortableIdentity).where(PortableIdentity.user_id == user_id)
        result = await db.execute(query)
        identity = result.scalar_one_or_none()
        
        if not identity:
            identity = PortableIdentity(user_id=user_id)
            db.add(identity)
            await db.commit()
            await db.refresh(identity)
            
        # Get skills
        skills_query = select(VerifiedSkill).where(VerifiedSkill.identity_id == identity.id)
        skills_result = await db.execute(skills_query)
        skills = skills_result.scalars().all()
        
        # Manually assemble response
        resp = PortableIdentityResponse.model_validate(identity)
        resp.skills = [VerifiedSkillSchema.model_validate(s) for s in skills]
        return resp

    @staticmethod
    async def update_identity(
        user_id: UUID,
        data: PortableIdentityUpdate,
        db: AsyncSession
    ) -> PortableIdentityResponse:
        query = select(PortableIdentity).where(PortableIdentity.user_id == user_id)
        result = await db.execute(query)
        identity = result.scalar_one_or_none()
        
        if not identity:
            raise ValueError("Identity not found")
            
        if data.visibility_projects:
            identity.visibility_projects = data.visibility_projects
        if data.visibility_achievements:
            identity.visibility_achievements = data.visibility_achievements
        if data.visibility_skills:
            identity.visibility_skills = data.visibility_skills
        if data.selective_sharing_workspaces is not None:
            identity.selective_sharing_workspaces = data.selective_sharing_workspaces
            
        await db.commit()
        await db.refresh(identity)
        
        # Get skills
        skills_query = select(VerifiedSkill).where(VerifiedSkill.identity_id == identity.id)
        skills_result = await db.execute(skills_query)
        skills = skills_result.scalars().all()
        
        resp = PortableIdentityResponse.model_validate(identity)
        resp.skills = [VerifiedSkillSchema.model_validate(s) for s in skills]
        return resp

    @staticmethod
    async def get_public_profile(user_id: UUID, requester_workspace_id: UUID, db: AsyncSession):
        # Enforce visibility rules
        # In a real system, we would query the user's projects/skills and filter them based on `visibility_tier`.
        pass
