from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.api_security import get_api_key, require_scopes
from app.services.data_exchange_service import DataExchangeService
from app.schemas.data_exchange import ExportRequest

router = APIRouter(prefix="/exchange", tags=["Data Exchange"])

@router.get("/export")
async def export_data(
    format: str = Query("json", description="json, csv, or ndjson"),
    include_hackathons: bool = Query(True),
    include_projects: bool = Query(True),
    include_organizations: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    api_key = Depends(require_scopes(["hackathons:read"])) # Adjust scope logic depending on entities
):
    if format not in ["json", "csv", "ndjson"]:
        raise HTTPException(status_code=400, detail="Unsupported format. Must be json, csv, or ndjson.")
        
    return await DataExchangeService.export_data(
        db=db,
        workspace_id=api_key.workspace_id,
        format=format,
        include_hackathons=include_hackathons,
        include_projects=include_projects,
        include_organizations=include_organizations
    )

from app.schemas.data_exchange import InnovationSchemaV1

@router.post("/import")
async def import_data(
    data: InnovationSchemaV1,
    db: AsyncSession = Depends(get_db),
    api_key = Depends(require_scopes(["hackathons:write"])) # Assuming they need write scope
):
    """
    Import InnovationSchema data into the workspace.
    """
    return await DataExchangeService.import_data(
        db=db,
        workspace_id=api_key.workspace_id,
        data=data
    )
