from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.schemas.opportunity import OpportunityMatchResponse
from app.services.opportunity_service import OpportunityService

router = APIRouter(
    prefix="/opportunities",
    tags=["opportunities"],
)

@router.get("/match", response_model=OpportunityMatchResponse)
async def get_opportunity_matches(
    workspace_id: uuid.UUID = Query(..., description="The ID of the active workspace"),
    entity_id: uuid.UUID = Query(..., description="The ID of the source entity"),
    entity_type: str = Query(..., description="The type of the source entity (e.g., Person, Team, Project)"),
    target_type: str = Query(..., description="The type of the opportunity to match against (e.g., Hackathon, Team, Organization)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated opportunity matches for a specific entity based on the graph relationships.
    """
    return await OpportunityService.match_opportunities(
        db=db,
        workspace_id=workspace_id,
        entity_id=entity_id,
        entity_type=entity_type,
        target_type=target_type
    )
