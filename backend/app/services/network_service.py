import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.network import NetworkResolveRequest, NetworkResolveResponse, NetworkNode, NetworkEdge

class NetworkService:
    @staticmethod
    async def resolve_network(
        workspace_id: uuid.UUID,
        request: NetworkResolveRequest,
        db: AsyncSession
    ) -> NetworkResolveResponse:
        from app.services.search_service import SearchService
        from app.services.graph_service import KnowledgeGraphService
        
        search_svc = SearchService(db)
        graph_svc = KnowledgeGraphService(db)
        
        # 1. Resolve seed nodes using semantic search
        search_result = await search_svc.search(workspace_id, request.query)
        
        if request.target_type:
            # Filter seeds by target_type
            seed_entities = [r for r in search_result.results if r.type == request.target_type]
        else:
            seed_entities = search_result.results
            
        seed_entities = seed_entities[:3] # Use top 3 as seeds
        
        nodes_dict = {}
        edges_list = []
        visited_edges = set()
        
        # 2. Traverse graph from seeds
        for seed in seed_entities:
            graph_data = await graph_svc.traverse(start_id=seed.id, workspace_id=workspace_id, depth=2)
            
            # Map nodes
            for n_id, n_info in graph_data.get("nodes", {}).items():
                if n_id not in nodes_dict:
                    data = n_info.get("data", {})
                    name = data.get("title") or data.get("name") or data.get("first_name") or f"Unknown {n_info['type']}"
                    nodes_dict[n_id] = NetworkNode(
                        id=n_id,
                        type=n_info["type"].lower(),
                        name=name,
                        metadata={"status": data.get("status"), "stage": data.get("stage")}
                    )
                    
            # Map edges
            for edge in graph_data.get("path", []):
                e_id = edge["id"]
                if e_id not in visited_edges:
                    visited_edges.add(e_id)
                    edges_list.append(NetworkEdge(
                        source=str(edge["source_id"]),
                        target=str(edge["target_id"]),
                        relation=edge["relation_type"]
                    ))
                    
        nodes = list(nodes_dict.values())
        
        ai_summary = None
        if request.include_impact_metrics:
            from app.services.ai.providers import AIProviderFactory
            from app.config import settings
            import json
            
            ai_provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY)
            
            # Serialize graph context for the LLM
            context = {
                "nodes": [{"name": n.name, "type": n.type} for n in nodes],
                "relationships": [{"source": e.source, "target": e.target, "relation": e.relation} for e in edges_list]
            }
            
            prompt = f"Analyze this innovation network graph and summarize the impact lifecycle for query: '{request.query}'. Context: {json.dumps(context)}"
            
            try:
                ai_summary = await ai_provider.generate_project_summary({"query": prompt})
            except Exception as e:
                ai_summary = f"Could not generate summary: {str(e)}"
            
        return NetworkResolveResponse(
            nodes=nodes,
            edges=edges_list,
            ai_summary=ai_summary
        )
