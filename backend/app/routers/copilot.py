from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.dependencies import verify_workspace_access
from app.schemas.copilot import CopilotQuery, CopilotResponse
from app.services.copilot_service import CopilotService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/copilot",
    tags=["ai_innovation_copilot"]
)

@router.post("/ask", response_model=CopilotResponse)
async def ask_copilot(
    workspace_id: UUID,
    query: CopilotQuery,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """
    Ask the AI Innovation Copilot a question.
    It uses intent detection to query the trusted knowledge graph in this workspace,
    and returns a verified answer with evidence and source entities.
    """
    return await CopilotService.ask_copilot(
        workspace_id=workspace_id,
        user_id=membership.user_id,
        query=query,
        db=db
    )
