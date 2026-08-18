import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, WorkspaceMembership
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse
from app.dependencies import get_current_user, verify_workspace_access

from app.schemas.digital_twin import DigitalTwinSimulationRequest, DigitalTwinSimulationResponse
from app.schemas.program_simulation import ProgramSimulationRequest, ProgramSimulationResponse

from app.services.digital_twin_service import DigitalTwinService
from app.services.program_simulation_service import ProgramSimulationService

router = APIRouter()

@router.get("/workspaces", response_model=list[WorkspaceResponse])
async def get_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Workspace)
        .join(WorkspaceMembership)
        .where(WorkspaceMembership.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/workspaces/{workspace_id}/digital-twin/simulate", response_model=DigitalTwinSimulationResponse)
async def simulate_digital_twin(
    workspace_id: uuid.UUID,
    request: DigitalTwinSimulationRequest,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    service = DigitalTwinService(db, current_user.id, workspace_id)
    return await service.run_simulation(request)

@router.post("/workspaces/{workspace_id}/program-simulation", response_model=ProgramSimulationResponse)
async def simulate_program_engine(
    workspace_id: uuid.UUID,
    request: ProgramSimulationRequest,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    service = ProgramSimulationService(db, current_user.id, workspace_id)
    return await service.run_simulation(request)

from app.schemas.operations_center import OperationsCenterStatus
from app.services.operations_center_service import OperationsCenterService

@router.get("/workspaces/{workspace_id}/operations-center", response_model=OperationsCenterStatus)
async def get_operations_center_status(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access),
    current_user: User = Depends(get_current_user)
):
    service = OperationsCenterService(db, current_user.id, workspace_id)
    return await service.get_status()
