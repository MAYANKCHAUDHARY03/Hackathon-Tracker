from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app.database import get_db
from app.schemas.innovation_protocol import InnovationProtocolExport
from app.services.innovation_protocol_service import InnovationProtocolService

router = APIRouter(
    prefix="/api/v1/protocol",
    tags=["innovation-protocol"],
    responses={404: {"description": "Not found"}},
)

@router.get("/export", response_model=InnovationProtocolExport)
async def export_protocol(
    db: AsyncSession = Depends(get_db)
):
    """
    Export all internal entities mapped to the platform-neutral Innovation Protocol.
    """
    service = InnovationProtocolService(db)
    return await service.export_ecosystem()

@router.post("/validate")
async def validate_protocol(
    payload: InnovationProtocolExport
):
    """
    Validate an Innovation Protocol payload without persisting it.
    If it passes Pydantic validation and reaches this point, it conforms to the schema.
    """
    return {"status": "valid", "object_count": len(payload.objects)}
