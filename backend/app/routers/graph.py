import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, get_db_ro
from app.dependencies import verify_workspace_access
from app.models.user import WorkspaceMembership
from app.schemas.graph import GraphEdgeCreate, GraphEdgeResponse, GraphTraversalResult
from app.services.graph_service import KnowledgeGraphService

router = APIRouter(prefix="/workspaces/{workspace_id}/graph", tags=["graph"])

@router.post("/edges", response_model=GraphEdgeResponse)
async def create_edge(
    workspace_id: uuid.UUID,
    edge_data: GraphEdgeCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    graph_service = KnowledgeGraphService(db)
    
    edge = await graph_service.create_edge(
        workspace_id=workspace_id,
        source_type=edge_data.source_type,
        source_id=edge_data.source_id,
        target_type=edge_data.target_type,
        target_id=edge_data.target_id,
        relation_type=edge_data.relation_type,
        properties=edge_data.properties,
        provenance=edge_data.provenance or "user-provided",
        confidence=edge_data.confidence or 1.0,
        created_by=membership.user_id,
        edge_edge_metadata=edge_data.edge_metadata
    )
    
    return edge

@router.post("/edges/{edge_id}/verify", response_model=GraphEdgeResponse)
async def verify_edge(
    workspace_id: uuid.UUID,
    edge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    # Depending on requirements, we might restrict verification to admins.
    # For now, any workspace member can verify.
    graph_service = KnowledgeGraphService(db)
    edge = await graph_service.verify_edge(
        edge_id=edge_id, 
        workspace_id=workspace_id, 
        user_id=membership.user_id
    )
    
    if not edge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")
        
    return edge

@router.get("/traverse/{node_id}", response_model=GraphTraversalResult)
async def traverse_graph(
    workspace_id: uuid.UUID,
    node_id: uuid.UUID,
    depth: int = 2,
    db: AsyncSession = Depends(get_db_ro),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    graph_service = KnowledgeGraphService(db)
    
    result = await graph_service.traverse(start_id=node_id, workspace_id=workspace_id, depth=depth)
    return result
