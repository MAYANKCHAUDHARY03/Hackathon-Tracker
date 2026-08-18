import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, verify_workspace_access
from app.models.user import User, WorkspaceMembership
from app.schemas.evaluation import EvaluationTemplateCreate, EvaluationTemplateUpdate, EvaluationTemplateResponse, EvaluationCriterionCreate, EvaluationCriterionResponse, EvaluationCreate, EvaluationUpdate, EvaluationResponse
from app.services import evaluation_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}/hackathons/{hackathon_id}",
    tags=["evaluations"]
)

@router.get("/evaluation-templates", response_model=List[EvaluationTemplateResponse])
async def list_templates(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    return await evaluation_service.get_templates(db, workspace_id, hackathon_id)

@router.post("/evaluation-templates", response_model=EvaluationTemplateResponse)
async def create_template(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    template_in: EvaluationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    template_in.hackathon_id = hackathon_id
    return await evaluation_service.create_template(db, workspace_id, current_user.id, template_in)

@router.post("/evaluation-templates/{template_id}/criteria", response_model=EvaluationCriterionResponse)
async def create_criterion(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    template_id: uuid.UUID,
    criterion_in: EvaluationCriterionCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await evaluation_service.create_criterion(db, workspace_id, template_id, criterion_in)

@router.post("/evaluations", response_model=EvaluationResponse)
async def create_evaluation(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    evaluation_in: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    evaluation_in.hackathon_id = hackathon_id
    return await evaluation_service.create_evaluation(db, workspace_id, current_user.id, evaluation_in)

@router.put("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    evaluation_id: uuid.UUID,
    evaluation_in: EvaluationUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    return await evaluation_service.update_evaluation(db, workspace_id, evaluation_id, current_user.id, evaluation_in)

from pydantic import BaseModel

class AgentEvaluationRequest(BaseModel):
    project_id: uuid.UUID
    template_id: uuid.UUID

@router.post("/agent-evaluation", response_model=EvaluationResponse)
async def generate_agent_evaluation(
    workspace_id: uuid.UUID,
    hackathon_id: uuid.UUID,
    request: AgentEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    from app.services.agent_evaluation_service import AgentEvaluationService
    service = AgentEvaluationService(db, current_user.id, workspace_id)
    return await service.generate_preliminary_evaluation(hackathon_id, request.project_id, request.template_id)

