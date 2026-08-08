import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class GraphEdge(BaseEntity):
    __tablename__ = "graph_edges"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    
    source_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    
    target_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    
    relation_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    properties: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_graph_edges_source", "source_type", "source_id"),
        Index("ix_graph_edges_target", "target_type", "target_id"),
        Index("ix_graph_edges_relation", "source_id", "relation_type", "target_id", unique=True),
    )
