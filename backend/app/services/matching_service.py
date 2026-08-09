import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.graph_service import GraphQueryService

class EcosystemMatchingEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.graph_service = GraphQueryService(db)

    async def compute_match_score(self, workspace_id: uuid.UUID, source_id: uuid.UUID, target_id: uuid.UUID) -> float:
        """
        Computes a match score between 0.0 and 1.0 for two unconnected entities based on shared attributes/edges.
        """
        # Get edges for source
        source_edges = await self.graph_service.get_edges(node_id=source_id, workspace_id=workspace_id, direction="both")
        
        # Get edges for target
        target_edges = await self.graph_service.get_edges(node_id=target_id, workspace_id=workspace_id, direction="both")
        
        # We look for common nodes they are connected to (e.g. skills, technologies, categories, problems)
        def get_connected_nodes(edges: List[Any], root_id: uuid.UUID) -> set:
            nodes = set()
            for edge in edges:
                if edge.source_id == root_id:
                    nodes.add(str(edge.target_id))
                else:
                    nodes.add(str(edge.source_id))
            return nodes

        source_connected = get_connected_nodes(source_edges, source_id)
        target_connected = get_connected_nodes(target_edges, target_id)
        
        if not source_connected or not target_connected:
            return 0.0
            
        intersection = source_connected.intersection(target_connected)
        union = source_connected.union(target_connected)
        
        if not union:
            return 0.0
            
        # Jaccard similarity
        score = len(intersection) / len(union)
        
        return score

    async def find_matches(self, workspace_id: uuid.UUID, source_id: uuid.UUID, target_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Finds best matches for a source entity against a specific target type in the graph.
        Since we don't have a pgvector index set up yet, we will traverse the graph and use shared edges.
        """
        # We can find all nodes of target_type in the workspace.
        # But this would require a DB query. Let's use the graph query service to find 2nd degree connections.
        
        # Get 2nd/3rd degree traversal from source
        traversal = await self.graph_service.traverse(start_id=source_id, workspace_id=workspace_id, depth=3)
        nodes = traversal.get("nodes", {})
        
        matches = []
        for node_str_id, info in nodes.items():
            if info["type"] == target_type and str(source_id) != node_str_id:
                target_uuid = uuid.UUID(node_str_id)
                score = await self.compute_match_score(workspace_id, source_id, target_uuid)
                if score > 0:
                    matches.append({
                        "node_id": node_str_id,
                        "type": target_type,
                        "score": score,
                        "data": info["data"]
                    })
                    
        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:limit]
