# pyrefly: ignore [missing-import]
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity
import typing

if typing.TYPE_CHECKING:
    from app.models.workspace import Workspace

class WorkspaceMembership(BaseEntity):
    __tablename__ = "workspace_memberships"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String, default="member")

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="memberships")

class User(BaseEntity):
    __tablename__ = "users"
    
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[str | None]
    github_handle: Mapped[str | None]
    linkedin_url: Mapped[str | None]
    
    memberships: Mapped[list["WorkspaceMembership"]] = relationship("WorkspaceMembership", back_populates="user", cascade="all, delete-orphan")
