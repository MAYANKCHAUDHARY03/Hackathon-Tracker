import uuid
from typing import List, Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper

from app.core.event_bus import event_bus
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
        
        # Publish event for Integrations
        await event_bus.publish("graph_edge_created", {
            "workspace_id": str(workspace_id),
            "source_type": source_type,
            "source_id": str(source_id),
            "target_type": target_type,
            "target_id": str(target_id),
            "relation_type": relation_type,
            "properties": properties or {}
        })
        
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

    async def get_workspace_portfolio(self, workspace_id: uuid.UUID) -> Dict[str, Any]:
        metrics = {
            "total_projects": 0,
            "active_projects": 0,
            "completed_projects": 0,
            "startups_spawned": 0,
            "patents_filed": 0,
            "top_technologies": [],
            "total_participants": 0
        }

        # 1. Projects
        project_stmt = select(Project).where(Project.workspace_id == workspace_id)
        projects = (await self.db.execute(project_stmt)).scalars().all()
        metrics["total_projects"] = len(projects)
        metrics["completed_projects"] = sum(1 for p in projects if p.status == "completed")
        metrics["active_projects"] = metrics["total_projects"] - metrics["completed_projects"]

        # 2. Edges for workspace
        edge_stmt = select(GraphEdge).where(GraphEdge.workspace_id == workspace_id)
        edges = (await self.db.execute(edge_stmt)).scalars().all()

        # 3. Startups & Patents (from edges)
        metrics["startups_spawned"] = sum(1 for e in edges if e.target_type == "Startup")
        metrics["patents_filed"] = sum(1 for e in edges if e.target_type == "Patent")

        # 4. Total participants (unique Users in graph)
        user_ids = set()
        for e in edges:
            if e.source_type == "User":
                user_ids.add(e.source_id)
            if e.target_type == "User":
                user_ids.add(e.target_id)
        metrics["total_participants"] = len(user_ids)

        # 5. Top technologies
        tech_edges = [e for e in edges if e.target_type == "Technology" and e.relation_type == "uses"]
        tech_counts = {}
        for e in tech_edges:
            tech_counts[e.target_id] = tech_counts.get(e.target_id, 0) + 1
        
        if tech_counts:
            from app.models.project import Technology
            tech_ids = list(tech_counts.keys())
            tech_stmt = select(Technology).where(Technology.id.in_(tech_ids))
            techs = (await self.db.execute(tech_stmt)).scalars().all()
            tech_map = {t.id: t.name for t in techs}
            
            top_techs = [{"name": tech_map.get(tid, str(tid)), "count": count} for tid, count in tech_counts.items()]
            top_techs.sort(key=lambda x: x["count"], reverse=True)
            metrics["top_technologies"] = top_techs[:5]

        return metrics
