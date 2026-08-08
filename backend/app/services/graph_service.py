import uuid
from typing import List, Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper

from app.models.graph import GraphEdge
from app.models.user import User
from app.models.team import Team
from app.models.project import Project
from app.models.hackathon import Hackathon
from app.models.organization import Organization
from app.models.people import Person
from app.models.challenge import Challenge
from app.models.startup import Startup
from app.models.sponsor import Sponsor

class GraphQueryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.type_to_model = {
            "User": User,
            "Team": Team,
            "Project": Project,
            "Hackathon": Hackathon,
            "Organization": Organization,
            "Person": Person,
            "Challenge": Challenge,
            "Startup": Startup,
            "Sponsor": Sponsor
        }

    async def get_node_by_type_and_id(self, node_type: str, node_id: uuid.UUID):
        model = self.type_to_model.get(node_type)
        if not model:
            return None
        result = await self.db.execute(select(model).where(model.id == node_id))
        return result.scalars().first()

    def serialize_node(self, node) -> Dict[str, Any]:
        if not node:
            return {}
        mapper = class_mapper(node.__class__)
        return {c.key: getattr(node, c.key) for c in mapper.columns}

    async def create_edge(
        self, 
        workspace_id: uuid.UUID,
        source_type: str, source_id: uuid.UUID, 
        target_type: str, target_id: uuid.UUID, 
        relation_type: str, properties: Dict[str, Any] = None
    ) -> GraphEdge:
        edge = GraphEdge(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {}
        )
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge

    async def get_edges(self, node_id: uuid.UUID, workspace_id: uuid.UUID, direction: str = "both") -> List[GraphEdge]:
        if direction == "out":
            stmt = select(GraphEdge).where(GraphEdge.source_id == node_id, GraphEdge.workspace_id == workspace_id)
        elif direction == "in":
            stmt = select(GraphEdge).where(GraphEdge.target_id == node_id, GraphEdge.workspace_id == workspace_id)
        else:
            stmt = select(GraphEdge).where(
                or_(GraphEdge.source_id == node_id, GraphEdge.target_id == node_id),
                GraphEdge.workspace_id == workspace_id
            )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def traverse(self, start_id: uuid.UUID, workspace_id: uuid.UUID, depth: int = 2) -> Dict[str, Any]:
        """
        Traverses the graph starting from start_id up to the specified depth.
        Returns a dictionary containing the path relationships and hydrated nodes.
        """
        visited_nodes = set()
        queue = [(start_id, 0)]
        edges_list = []
        nodes_dict = {}

        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited_nodes:
                continue
            
            visited_nodes.add(current_id)

            if current_depth < depth:
                # Get all edges where current_id is source or target
                edges = await self.get_edges(current_id, workspace_id, direction="both")
                for edge in edges:
                    edges_list.append({
                        "id": str(edge.id),
                        "source_type": edge.source_type,
                        "source_id": str(edge.source_id),
                        "target_type": edge.target_type,
                        "target_id": str(edge.target_id),
                        "relation_type": edge.relation_type,
                        "properties": edge.properties
                    })
                    
                    next_id = edge.target_id if edge.source_id == current_id else edge.source_id
                    queue.append((next_id, current_depth + 1))
                    
                    # Store node types for hydration
                    if str(edge.source_id) not in nodes_dict:
                        nodes_dict[str(edge.source_id)] = {"type": edge.source_type, "id": edge.source_id}
                    if str(edge.target_id) not in nodes_dict:
                        nodes_dict[str(edge.target_id)] = {"type": edge.target_type, "id": edge.target_id}

        # Hydrate nodes
        hydrated_nodes = {}
        for node_str_id, info in nodes_dict.items():
            node = await self.get_node_by_type_and_id(info["type"], info["id"])
            if node:
                hydrated = self.serialize_node(node)
                # Convert UUIDs/datetimes for JSON serialization safely
                for k, v in hydrated.items():
                    if isinstance(v, uuid.UUID):
                        hydrated[k] = str(v)
                    elif isinstance(v, datetime):
                        hydrated[k] = v.isoformat()
                
                hydrated_nodes[node_str_id] = {
                    "type": info["type"],
                    "data": hydrated
                }

        return {
            "path": edges_list,
            "nodes": hydrated_nodes
        }
