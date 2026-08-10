import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime

from app.models.incubation import ProjectUpdate, ProjectDocument, ProjectFunding, ProjectUpdateType, ProjectDocumentType
from app.models.graph import GraphEdge
from app.models.kanban import Task
from app.models.user import User
from app.schemas.incubation import (
    ProjectUpdateCreate,
    ProjectDocumentCreate,
    ProjectFundingCreate,
    IncubationDashboardResponse,
    ProjectUpdateResponse,
    ProjectDocumentResponse,
    ProjectFundingResponse,
    StakeholderResponse
)

class IncubationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, project_id: uuid.UUID) -> IncubationDashboardResponse:
        # 1. Fetch updates
        stmt_updates = select(ProjectUpdate).where(ProjectUpdate.project_id == project_id).order_by(desc(ProjectUpdate.created_at))
        result_updates = await self.db.execute(stmt_updates)
        updates = result_updates.scalars().all()

        # 2. Fetch documents
        stmt_docs = select(ProjectDocument).where(ProjectDocument.project_id == project_id).order_by(desc(ProjectDocument.created_at))
        result_docs = await self.db.execute(stmt_docs)
        documents = result_docs.scalars().all()

        # 3. Fetch funding rounds
        stmt_funding = select(ProjectFunding).where(ProjectFunding.project_id == project_id).order_by(desc(ProjectFunding.date))
        result_funding = await self.db.execute(stmt_funding)
        funding_rounds = result_funding.scalars().all()

        # 4. Fetch stakeholders from GraphEdge (mentors, advises, invests_in) -> User
        stmt_edges = select(GraphEdge).where(
            GraphEdge.target_id == project_id,
            GraphEdge.target_type == "project",
            GraphEdge.source_type == "user",
            GraphEdge.relation_type.in_(["mentors", "advises", "invests_in"])
        )
        result_edges = await self.db.execute(stmt_edges)
        edges = result_edges.scalars().all()

        stakeholders = []
        if edges:
            user_ids = [edge.source_id for edge in edges]
            stmt_users = select(User).where(User.id.in_(user_ids))
            result_users = await self.db.execute(stmt_users)
            users = {u.id: u for u in result_users.scalars().all()}

            for edge in edges:
                user = users.get(edge.source_id)
                if user:
                    stakeholders.append(
                        StakeholderResponse(
                            user_id=user.id,
                            name=user.full_name,
                            email=user.email,
                            avatar_url=user.avatar_url,
                            role=edge.relation_type
                        )
                    )

        # Map to responses
        updates_resp = [ProjectUpdateResponse.model_validate(u) for u in updates]
        docs_resp = [ProjectDocumentResponse.model_validate(d) for d in documents]
        funding_resp = [ProjectFundingResponse.model_validate(f) for f in funding_rounds]

        return IncubationDashboardResponse(
            project_id=project_id,
            updates=updates_resp,
            documents=docs_resp,
            funding_rounds=funding_resp,
            stakeholders=stakeholders
        )

    async def create_update(self, project_id: uuid.UUID, data: ProjectUpdateCreate, author_id: Optional[uuid.UUID] = None) -> ProjectUpdateResponse:
        update = ProjectUpdate(
            project_id=project_id,
            author_id=author_id,
            update_type=data.update_type,
            title=data.title,
            content=data.content,
            kpi_metrics=data.kpi_metrics
        )
        self.db.add(update)
        await self.db.commit()
        await self.db.refresh(update)
        return ProjectUpdateResponse.model_validate(update)

    async def create_document(self, project_id: uuid.UUID, data: ProjectDocumentCreate, uploaded_by_id: Optional[uuid.UUID] = None) -> ProjectDocumentResponse:
        doc = ProjectDocument(
            project_id=project_id,
            uploaded_by_id=uploaded_by_id,
            title=data.title,
            document_type=data.document_type,
            url=data.url
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return ProjectDocumentResponse.model_validate(doc)

    async def create_funding_round(self, project_id: uuid.UUID, data: ProjectFundingCreate) -> ProjectFundingResponse:
        funding = ProjectFunding(
            project_id=project_id,
            round_type=data.round_type,
            amount=data.amount,
            currency=data.currency,
            date=data.date,
            investors=data.investors
        )
        self.db.add(funding)
        await self.db.commit()
        await self.db.refresh(funding)
        return ProjectFundingResponse.model_validate(funding)

    async def add_stakeholder(self, workspace_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
        edge = GraphEdge(
            workspace_id=workspace_id,
            source_type="user",
            source_id=user_id,
            target_type="project",
            target_id=project_id,
            relation_type=role
        )
        self.db.add(edge)
        await self.db.commit()
