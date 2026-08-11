import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import BaseEntity


class OAuthApp(BaseEntity):
    __tablename__ = "oauth_apps"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    homepage_url: Mapped[str | None] = mapped_column(String, nullable=True)
    callback_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    
    client_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    client_secret_hash: Mapped[str] = mapped_column(String)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class APIKey(BaseEntity):
    __tablename__ = "api_keys"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Can be linked to an OAuthApp or stand-alone for personal access
    oauth_app_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("oauth_apps.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String)
    prefix: Mapped[str] = mapped_column(String, index=True)  # Store prefix like 'ht_live_' or 'ht_test_'
    key_hash: Mapped[str] = mapped_column(String, unique=True, index=True) # Hashed API key
    
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list) # e.g. ["projects:read", "hackathons:write"]
    
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
