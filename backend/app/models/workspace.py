from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON
from app.models.base import BaseEntity
import typing

if typing.TYPE_CHECKING:
    from app.models.user import WorkspaceMembership

class Workspace(BaseEntity):
    __tablename__ = "workspaces"
    
    name: Mapped[str] = mapped_column(index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    memberships: Mapped[list["WorkspaceMembership"]] = relationship("WorkspaceMembership", back_populates="workspace", cascade="all, delete-orphan")
