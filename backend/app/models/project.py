import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseEntity

class Project(BaseEntity):
    __tablename__ = "projects"

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hackathons.id", ondelete="CASCADE"), index=True)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), unique=True, index=True)
    
    title: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, index=True)
    problem_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    repository_url: Mapped[str | None] = mapped_column(String, nullable=True)
    demo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    documentation_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="idea", index=True)
    
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("hackathon_id", "slug", name="uq_project_slug_per_hackathon"),
    )

    workspace = relationship("Workspace")
    hackathon = relationship("Hackathon")
    team = relationship("Team")
    creator = relationship("User")
    technologies = relationship("ProjectTechnology", back_populates="project", cascade="all, delete-orphan")


class Technology(BaseEntity):
    __tablename__ = "technologies"

    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    category: Mapped[str] = mapped_column(String, index=True)


class ProjectTechnology(BaseEntity):
    __tablename__ = "project_technologies"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    technology_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("technologies.id", ondelete="CASCADE"), index=True)
    
    version: Mapped[str | None] = mapped_column(String, nullable=True)
    purpose: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("project_id", "technology_id", name="uq_technology_per_project"),
    )

    project = relationship("Project", back_populates="technologies")
    technology = relationship("Technology")
