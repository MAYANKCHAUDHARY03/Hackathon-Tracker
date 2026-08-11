import uuid
from typing import List, Dict, Any, Set
from datetime import datetime, timezone
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper

from app.core.event_bus import event_bus
from app.models.graph import GraphEdge, EdgeProvenance
from app.models.user import User
from app.models.team import Team
from app.models.project import Project
from app.models.hackathon import Hackathon
from app.models.organization import Organization
from app.models.people import Person
from app.models.challenge import Challenge
from app.models.startup import Startup
from app.models.sponsor import Sponsor


class KnowledgeGraphService:
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

    async def get_nodes_by_type_and_ids(self, node_type: str, node_ids: List[uuid.UUID]):
        model = self.type_to_model.get(node_type)
        if not model or not node_ids:
            return []
        result = await self.db.execute(select(model).where(model.id.in_(node_ids)))
        return result.scalars().all()

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
        relation_type: str, 
        properties: Dict[str, Any] = None,
        provenance: str = EdgeProvenance.user_provided.value,
        confidence: float = 1.0,
        created_by: uuid.UUID = None,
        edge_metadata: Dict[str, Any] = None
    ) -> GraphEdge:
        
        # Check for existing edge
        stmt = select(GraphEdge).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.source_id == source_id,
            GraphEdge.target_id == target_id,
            GraphEdge.relation_type == relation_type
        )
        existing = (await self.db.execute(stmt)).scalars().first()
        if existing:
            return existing

        edge = GraphEdge(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {},
            provenance=provenance,
            confidence=confidence,
            created_by=created_by,
            edge_edge_metadata=edge_metadata or {}
        )
        
        # If it's created as verified, set verification fields
        if provenance == EdgeProvenance.verified.value and created_by:
            edge.verified_at = datetime.now(timezone.utc)
            edge.verified_by = created_by

        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        
        # Publish event for Integrations
        await event_bus.publish("graph_edge_created", {
            "workspace_id": str(workspace_id),
            "edge_id": str(edge.id),
            "source_type": source_type,
            "source_id": str(source_id),
            "target_type": target_type,
            "target_id": str(target_id),
            "relation_type": relation_type,
            "provenance": provenance
        })
        
        return edge

    async def verify_edge(self, edge_id: uuid.UUID, workspace_id: uuid.UUID, user_id: uuid.UUID) -> GraphEdge:
        stmt = select(GraphEdge).where(GraphEdge.id == edge_id, GraphEdge.workspace_id == workspace_id)
        edge = (await self.db.execute(stmt)).scalars().first()
        if not edge:
            return None
            
        edge.provenance = EdgeProvenance.verified.value
        edge.confidence = 1.0
        edge.verified_at = datetime.now(timezone.utc)
        edge.verified_by = user_id
        
        await self.db.commit()
        await self.db.refresh(edge)
        return edge

    async def traverse(self, start_id: uuid.UUID, workspace_id: uuid.UUID, depth: int = 2) -> Dict[str, Any]:
        """
        Traverses the graph using level-based batch fetching to avoid N+1 queries.
        Returns a dictionary containing the path relationships and hydrated nodes.
        """
        visited_nodes = {start_id}
        current_level_nodes = {start_id}
        edges_list = []
        nodes_dict = {str(start_id): {"type": "Unknown", "id": start_id}} # We will correct type later if needed
        
        all_edges_seen = set()

        for current_depth in range(depth):
            if not current_level_nodes:
                break
                
            # Batch fetch all edges for current level nodes
            stmt = select(GraphEdge).where(
                or_(
                    GraphEdge.source_id.in_(current_level_nodes), 
                    GraphEdge.target_id.in_(current_level_nodes)
                ),
                GraphEdge.workspace_id == workspace_id
            )
            edges = (await self.db.execute(stmt)).scalars().all()
            
            next_level_nodes = set()
            
            for edge in edges:
                if edge.id in all_edges_seen:
                    continue
                all_edges_seen.add(edge.id)
                
                edges_list.append({
                    "id": str(edge.id),
                    "source_type": edge.source_type,
                    "source_id": str(edge.source_id),
                    "target_type": edge.target_type,
                    "target_id": str(edge.target_id),
                    "relation_type": edge.relation_type,
                    "properties": edge.properties,
                    "provenance": edge.provenance,
                    "confidence": edge.confidence
                })
                
                # Identify next nodes to traverse
                next_id = edge.target_id if edge.source_id in current_level_nodes else edge.source_id
                if next_id not in visited_nodes:
                    next_level_nodes.add(next_id)
                    visited_nodes.add(next_id)
                
                # Register node types
                nodes_dict[str(edge.source_id)] = {"type": edge.source_type, "id": edge.source_id}
                nodes_dict[str(edge.target_id)] = {"type": edge.target_type, "id": edge.target_id}
                
            current_level_nodes = next_level_nodes

        # Batch hydrate nodes grouped by type
        hydrated_nodes = {}
        nodes_by_type = {}
        for str_id, info in nodes_dict.items():
            if info["type"] == "Unknown":
                continue
            nodes_by_type.setdefault(info["type"], []).append(info["id"])
            
        for n_type, n_ids in nodes_by_type.items():
            nodes = await self.get_nodes_by_type_and_ids(n_type, n_ids)
            for node in nodes:
                hydrated = self.serialize_node(node)
                # Convert UUIDs/datetimes for JSON serialization safely
                for k, v in hydrated.items():
                    if isinstance(v, uuid.UUID):
                        hydrated[k] = str(v)
                    elif isinstance(v, datetime):
                        hydrated[k] = v.isoformat()
                        
                # Strip PII (Privacy Audit requirement)
                if n_type == "User" or n_type == "Person":
                    hydrated.pop("email", None)
                    hydrated.pop("phone", None)
                    hydrated.pop("password_hash", None)
                
                hydrated_nodes[str(node.id)] = {
                    "type": n_type,
                    "data": hydrated
                }

        return {
            "path": edges_list,
            "nodes": hydrated_nodes
        }

    async def get_workspace_portfolio(self, workspace_id: uuid.UUID) -> Dict[str, Any]:
        # Using optimized aggregate queries
        metrics = {
            "total_projects": 0,
            "active_projects": 0,
            "completed_projects": 0,
            "startups_spawned": 0,
            "patents_filed": 0,
            "top_technologies": [],
            "total_participants": 0
        }

        # 1. Projects (aggregate)
        stmt_proj = select(Project.status, func.count(Project.id)).where(Project.workspace_id == workspace_id).group_by(Project.status)
        proj_counts = (await self.db.execute(stmt_proj)).all()
        for status, count in proj_counts:
            metrics["total_projects"] += count
            if status == "completed":
                metrics["completed_projects"] += count
            else:
                metrics["active_projects"] += count

        # 2. Startups & Patents (from edges)
        stmt_outcomes = select(GraphEdge.target_type, func.count(GraphEdge.id)).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.target_type.in_(["Startup", "Patent"])
        ).group_by(GraphEdge.target_type)
        
        outcome_counts = (await self.db.execute(stmt_outcomes)).all()
        for t_type, count in outcome_counts:
            if t_type == "Startup":
                metrics["startups_spawned"] = count
            elif t_type == "Patent":
                metrics["patents_filed"] = count

        # 3. Total participants (unique Users connected to workspace)
        stmt_users = select(func.count(func.distinct(GraphEdge.source_id))).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.source_type == "User"
        )
        metrics["total_participants"] = (await self.db.execute(stmt_users)).scalar() or 0

        # 4. Top technologies
        stmt_tech = select(GraphEdge.target_id, func.count(GraphEdge.id).label("cnt")).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.target_type == "Technology",
            GraphEdge.relation_type == "uses"
        ).group_by(GraphEdge.target_id).order_by(func.count(GraphEdge.id).desc()).limit(5)
        
        top_tech_rows = (await self.db.execute(stmt_tech)).all()
        if top_tech_rows:
            from app.models.project import Technology
            tech_ids = [row[0] for row in top_tech_rows]
            tech_map_stmt = select(Technology.id, Technology.name).where(Technology.id.in_(tech_ids))
            techs = (await self.db.execute(tech_map_stmt)).all()
            tech_map = {t_id: name for t_id, name in techs}
            
            metrics["top_technologies"] = [{"name": tech_map.get(row[0], str(row[0])), "count": row[1]} for row in top_tech_rows]

        return metrics
