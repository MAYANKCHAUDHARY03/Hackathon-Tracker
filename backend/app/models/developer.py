import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
import secrets

from app.models.base import BaseEntity

class DeveloperApp(BaseEntity):
    __tablename__ = "developer_apps"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String)
    
    client_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    client_secret: Mapped[str] = mapped_column(String)
    
    redirect_uris: Mapped[list] = mapped_column(JSON, default=list)

class WebhookEndpoint(BaseEntity):
    __tablename__ = "webhook_endpoints"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String)
    events: Mapped[list] = mapped_column(JSON, default=list) # e.g. ["project.created", "project.updated"]
    secret: Mapped[str] = mapped_column(String)
