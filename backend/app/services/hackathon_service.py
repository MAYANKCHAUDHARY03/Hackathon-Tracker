from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.hackathon import Hackathon
from app.schemas.hackathon import HackathonCreate, HackathonUpdate

class HackathonService:
    @staticmethod
    async def create_hackathon(
        db: AsyncSession,
        workspace_id: UUID,
        user_id: UUID,
        hackathon_data: HackathonCreate
    ) -> Hackathon:
        hackathon = Hackathon(
            **hackathon_data.model_dump(exclude_unset=True),
            workspace_id=workspace_id,
            created_by=user_id,
            status=hackathon_data.status or "draft"
        )
        db.add(hackathon)
        await db.commit()
        await db.refresh(hackathon)
        return hackathon

    @staticmethod
    async def get_hackathons(
        db: AsyncSession,
        workspace_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        mode: str | None = None,
        status_filter: str | None = None,
        include_archived: bool = False,
        is_template: bool | None = None
    ) -> tuple[list[Hackathon], int]:
        conditions = [Hackathon.workspace_id == workspace_id]
        
        if is_template is not None:
            conditions.append(Hackathon.is_template == is_template)
        
        if not include_archived:
            conditions.append(Hackathon.archived_at.is_(None))
            
        if mode:
            conditions.append(Hackathon.mode == mode)
            
        if status_filter:
            conditions.append(Hackathon.status == status_filter)
            
        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    Hackathon.name.ilike(search_term),
                    Hackathon.organiser.ilike(search_term)
                )
            )
            
        stmt = select(Hackathon).where(and_(*conditions))
        
        # total count
        count_stmt = select(func.count()).select_from(Hackathon).where(and_(*conditions))
        total = (await db.execute(count_stmt)).scalar() or 0
        
        # default sort by start_date asc
        stmt = stmt.order_by(asc(Hackathon.start_date)).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_hackathon_by_id(
        db: AsyncSession,
        workspace_id: UUID,
        hackathon_id: UUID
    ) -> Hackathon:
        stmt = select(Hackathon).where(
            Hackathon.id == hackathon_id,
            Hackathon.workspace_id == workspace_id
        )
        result = await db.execute(stmt)
        hackathon = result.scalar_one_or_none()
        
        if not hackathon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hackathon not found"
            )
            
        return hackathon

    @staticmethod
    async def update_hackathon(
        db: AsyncSession,
        workspace_id: UUID,
        hackathon_id: UUID,
        hackathon_data: HackathonUpdate
    ) -> Hackathon:
        hackathon = await HackathonService.get_hackathon_by_id(db, workspace_id, hackathon_id)
        
        update_dict = hackathon_data.model_dump(exclude_unset=True)
        if not update_dict:
            return hackathon
            
        # Cross-field date validation on partial updates
        new_start = update_dict.get('start_date', hackathon.start_date)
        new_end = update_dict.get('end_date', hackathon.end_date)
        new_reg = update_dict.get('registration_deadline', hackathon.registration_deadline)
        
        # In python, datetime might be naive or aware, but we assume timezone-aware
        if new_end < new_start:
            raise HTTPException(status_code=422, detail="end_date cannot be earlier than start_date")
        if new_reg > new_start:
            raise HTTPException(status_code=422, detail="registration_deadline must be before or equal to start_date")
            
        # Location validation
        new_mode = update_dict.get('mode', hackathon.mode)
        new_location = update_dict.get('location', hackathon.location)
        if new_mode in {"offline", "hybrid"} and not new_location:
            raise HTTPException(status_code=422, detail=f"location is required for mode '{new_mode}'")
            
        for key, value in update_dict.items():
            setattr(hackathon, key, value)
            
        await db.commit()
        await db.refresh(hackathon)
        return hackathon

    @staticmethod
    async def archive_hackathon(
        db: AsyncSession,
        workspace_id: UUID,
        hackathon_id: UUID
    ) -> Hackathon:
        hackathon = await HackathonService.get_hackathon_by_id(db, workspace_id, hackathon_id)
        if not hackathon.archived_at:
            hackathon.archived_at = datetime.now(timezone.utc)
            hackathon.status = "archived"
            await db.commit()
            await db.refresh(hackathon)
        return hackathon

    @staticmethod
    async def restore_hackathon(
        db: AsyncSession,
        workspace_id: UUID,
        hackathon_id: UUID
    ) -> Hackathon:
        hackathon = await HackathonService.get_hackathon_by_id(db, workspace_id, hackathon_id)
        if hackathon.archived_at:
            hackathon.archived_at = None
            hackathon.status = "draft"  # or restore to a previous state, default to draft
            await db.commit()
            await db.refresh(hackathon)
        return hackathon

    @staticmethod
    async def delete_hackathon(
        db: AsyncSession,
        workspace_id: UUID,
        hackathon_id: UUID
    ):
        hackathon = await HackathonService.get_hackathon_by_id(db, workspace_id, hackathon_id)
        await db.delete(hackathon)
        await db.commit()

    @staticmethod
    async def create_from_template(
        db: AsyncSession,
        workspace_id: UUID,
        user_id: UUID,
        template_id: UUID,
        hackathon_data: HackathonCreate
    ) -> Hackathon:
        template = await HackathonService.get_hackathon_by_id(db, workspace_id, template_id)
        if not template.is_template:
            raise HTTPException(status_code=400, detail="Requested program is not a template")
            
        hackathon = Hackathon(
            **hackathon_data.model_dump(exclude_unset=True),
            workspace_id=workspace_id,
            created_by=user_id,
            status=hackathon_data.status or "draft",
            program_type=template.program_type,
            is_template=False
        )
        db.add(hackathon)
        
        # Note: in a real production system we would also clone rounds and deadlines here
        # based on the template's rounds and deadlines.
        
        await db.commit()
        await db.refresh(hackathon)
        return hackathon
