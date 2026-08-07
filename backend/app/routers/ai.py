from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.models.project import Project
from app.models.kanban import Task
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.ai import AIProjectSummaryResponse, AIHealthAnalysisResponse
from app.services.ai import AIProviderFactory
from app.config import settings

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/ai",
    tags=["ai_intelligence"]
)

@router.get("/summary", response_model=AIProjectSummaryResponse)
async def get_project_summary(
    workspace_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """Generate an AI summary for a project."""
    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    provider = AIProviderFactory.get_provider("mock", "dummy_key")
    
    project_data = {
        "title": project.name,
        "description": project.description,
        "repo_url": project.repository_url
    }
    
    summary = await provider.generate_project_summary(project_data)
    return AIProjectSummaryResponse(summary=summary)

@router.get("/health", response_model=AIHealthAnalysisResponse)
async def analyze_project_health(
    workspace_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Analyze project health using AI and deterministic algorithms."""
    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    task_query = select(Task).join(Task.column).where(
        Task.project_id == project_id
    )
    task_result = await db.execute(task_query)
    tasks = task_result.scalars().all()
    
    task_list = [
        {"title": t.title, "status": t.column.name if t.column else "unknown", "priority": t.priority} 
        for t in tasks
    ]
    
    provider = AIProviderFactory.get_provider("mock", "dummy_key")
    
    project_data = {
        "title": project.name,
        "description": project.description
    }
    
    analysis = await provider.analyze_project_health(project_data, task_list)
    return AIHealthAnalysisResponse(**analysis)
