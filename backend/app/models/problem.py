import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, cast, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.ontology import UniversalEntity, EntityType

class Problem(UniversalEntity):
    __mapper_args__ = {
        "polymorphic_identity": EntityType.PROBLEM
    }

    # Instead of separate columns, map to properties JSON
    @hybrid_property
    def title(self) -> str:
        return self.properties.get("title", "")
    
    @title.inplace.setter
    def _title_setter(self, value: str):
        self.properties = {**self.properties, "title": value}

    @title.inplace.expression
    @classmethod
    def title(cls):
        return func.trim(cast(cls.properties["title"], String), '"')

    @hybrid_property
    def slug(self) -> str:
        return self.properties.get("slug", "")

    @slug.inplace.setter
    def _slug_setter(self, value: str):
        self.properties = {**self.properties, "slug": value}

    @slug.inplace.expression
    @classmethod
    def slug(cls):
        return func.trim(cast(cls.properties["slug"], String), '"')
        
    @hybrid_property
    def description(self) -> str:
        return self.properties.get("description", "")
        
    @description.inplace.setter
    def _description_setter(self, value: str):
        self.properties = {**self.properties, "description": value}

    @description.inplace.expression
    @classmethod
    def description(cls):
        return func.trim(cast(cls.properties["description"], String), '"')
        
    @hybrid_property
    def domain(self) -> str:
        return self.properties.get("domain", None)
        
    @domain.inplace.setter
    def _domain_setter(self, value: str):
        self.properties = {**self.properties, "domain": value}

    @domain.inplace.expression
    @classmethod
    def domain(cls):
        return func.trim(cast(cls.properties["domain"], String), '"')

    @hybrid_property
    def impact_potential(self) -> str:
        return self.properties.get("impact_potential", None)
        
    @impact_potential.inplace.setter
    def _impact_potential_setter(self, value: str):
        self.properties = {**self.properties, "impact_potential": value}

    @impact_potential.inplace.expression
    @classmethod
    def impact_potential(cls):
        return func.trim(cast(cls.properties["impact_potential"], String), '"')
        
    @hybrid_property
    def status(self) -> str:
        return self.properties.get("status", "open")
        
    @status.inplace.setter
    def _status_setter(self, value: str):
        self.properties = {**self.properties, "status": value}

    @status.inplace.expression
    @classmethod
    def status(cls):
        return func.trim(cast(cls.properties["status"], String), '"')

    @hybrid_property
    def created_by(self) -> str:
        return self.properties.get("created_by", None)
        
    @created_by.inplace.setter
    def _created_by_setter(self, value: str):
        self.properties = {**self.properties, "created_by": str(value) if value else None}

    @created_by.inplace.expression
    @classmethod
    def created_by(cls):
        return func.trim(cast(cls.properties["created_by"], String), '"')

    workspace = relationship("Workspace", foreign_keys="UniversalEntity.workspace_id")
