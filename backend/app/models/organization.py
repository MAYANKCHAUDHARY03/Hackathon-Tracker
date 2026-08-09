from sqlalchemy import String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity
import typing
import uuid

if typing.TYPE_CHECKING:
    from app.models.user import User
    from app.models.workspace import Workspace

class Organization(BaseEntity):
    __tablename__ = "organizations"
    
    name: Mapped[str] = mapped_column(index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[str] = mapped_column(String, default="active")
    timezone: Mapped[str] = mapped_column(String, default="UTC")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    ecosystem_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)

    memberships: Mapped[list["OrganizationMembership"]] = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    workspaces: Mapped[list["Workspace"]] = relationship("Workspace", back_populates="organization")

class OrganizationMembership(BaseEntity):
    __tablename__ = "organization_memberships"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String, default="member")
    status: Mapped[str] = mapped_column(String, default="active")

    user: Mapped["User"] = relationship("User", back_populates="organization_memberships")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="memberships")
