from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, ForeignKey
import uuid
from app.models.base import BaseEntity
import typing

if typing.TYPE_CHECKING:
    from app.models.user import WorkspaceMembership
    from app.models.organization import Organization

class Workspace(BaseEntity):
    __tablename__ = "workspaces"
    
    name: Mapped[str] = mapped_column(index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True)

    organization: Mapped["Organization | None"] = relationship("Organization", back_populates="workspaces")

    memberships: Mapped[list["WorkspaceMembership"]] = relationship("WorkspaceMembership", back_populates="workspace", cascade="all, delete-orphan")
