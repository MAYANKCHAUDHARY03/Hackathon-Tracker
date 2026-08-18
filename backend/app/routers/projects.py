from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectTransitionCreate, ProjectTransition
from app.services import project_service

router = APIRouter()

@router.get("/workspaces/{workspace_id}/projects", response_model=list[ProjectResponse])
async def get_projects(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.get_projects(db, workspace_id)

@router.post("/workspaces/{workspace_id}/teams/{team_id}/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: uuid.UUID,
    team_id: uuid.UUID,
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.create_project(db, workspace_id, team_id, project_in, current_user)

@router.post("/workspaces/{workspace_id}/projects/{project_id}/transitions", response_model=ProjectResponse)
async def transition_project_state(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    transition_in: ProjectTransitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.transition_project_state(
        db, workspace_id, project_id, transition_in.state, current_user, transition_in.notes or ""
    )

@router.get("/workspaces/{workspace_id}/projects/{project_id}/transitions", response_model=list[ProjectTransition])
async def get_project_transitions(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.get_project_transitions(db, workspace_id, project_id)

from app.schemas.project_copilot import ProjectCopilotStatus, CopilotActionRequest
from app.services.project_copilot_service import ProjectCopilotService

@router.get("/workspaces/{workspace_id}/projects/{project_id}/copilot", response_model=ProjectCopilotStatus)
async def get_project_copilot_status(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProjectCopilotService(db, current_user.id, workspace_id)
    return await service.get_project_status(project_id)

@router.post("/workspaces/{workspace_id}/projects/{project_id}/copilot/action")
async def execute_project_copilot_action(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    action_req: CopilotActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProjectCopilotService(db, current_user.id, workspace_id)
    return await service.execute_action(project_id, action_req.action)

from app.schemas.mentor_copilot import MentorCopilotBrief
from app.services.mentor_copilot_service import MentorCopilotService

@router.get("/workspaces/{workspace_id}/projects/{project_id}/mentor-copilot", response_model=MentorCopilotBrief)
async def get_mentor_copilot_brief(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = MentorCopilotService(db, current_user.id, workspace_id)
    return await service.generate_brief(project_id)

from app.schemas.repository_audit import RepositoryAuditResponse
from app.services.repository_audit_service import RepositoryAuditService

@router.post("/workspaces/{workspace_id}/projects/{project_id}/audit", response_model=RepositoryAuditResponse)
async def generate_repository_audit(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RepositoryAuditService(db, current_user.id, workspace_id)
    return await service.generate_audit(project_id)

@router.get("/workspaces/{workspace_id}/projects/{project_id}/audits", response_model=list[RepositoryAuditResponse])
async def get_repository_audits(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RepositoryAuditService(db, current_user.id, workspace_id)
    return await service.get_audits_for_project(project_id)
