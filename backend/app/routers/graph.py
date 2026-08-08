import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import verify_workspace_access
from app.models.user import WorkspaceMembership
from app.schemas.graph import GraphEdgeCreate, GraphEdgeResponse, GraphTraversalResult
from app.services.graph_service import GraphQueryService

router = APIRouter(prefix="/workspaces/{workspace_id}/graph", tags=["graph"])

@router.post("/edges", response_model=GraphEdgeResponse)
async def create_edge(
    workspace_id: uuid.UUID,
    edge_data: GraphEdgeCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    graph_service = GraphQueryService(db)
    
    edge = await graph_service.create_edge(
        workspace_id=workspace_id,
        source_type=edge_data.source_type,
        source_id=edge_data.source_id,
        target_type=edge_data.target_type,
        target_id=edge_data.target_id,
        relation_type=edge_data.relation_type,
        properties=edge_data.properties
    )
    
    return edge

@router.get("/traverse/{node_id}", response_model=GraphTraversalResult)
async def traverse_graph(
    workspace_id: uuid.UUID,
    node_id: uuid.UUID,
    depth: int = 2,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    graph_service = GraphQueryService(db)
    
    result = await graph_service.traverse(start_id=node_id, workspace_id=workspace_id, depth=depth)
    return result
