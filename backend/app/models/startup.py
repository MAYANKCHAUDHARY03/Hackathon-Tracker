import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, cast, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.ontology import UniversalEntity, EntityType

class Startup(UniversalEntity):
    __mapper_args__ = {
        "polymorphic_identity": EntityType.STARTUP
    }

    @hybrid_property
    def name(self) -> str:
        return self.properties.get("name", "")
        
    @name.inplace.setter
    def _name_setter(self, value: str):
        self.properties = {**self.properties, "name": value}

    @name.inplace.expression
    @classmethod
    def name(cls):
        return func.trim(cast(cls.properties["name"], String), '"')

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
    def website_url(self) -> str:
        return self.properties.get("website_url", None)

    @website_url.inplace.setter
    def _website_url_setter(self, value: str):
        self.properties = {**self.properties, "website_url": value}

    @website_url.inplace.expression
    @classmethod
    def website_url(cls):
        return func.trim(cast(cls.properties["website_url"], String), '"')

    @hybrid_property
    def industry(self) -> str:
        return self.properties.get("industry", None)

    @industry.inplace.setter
    def _industry_setter(self, value: str):
        self.properties = {**self.properties, "industry": value}

    @industry.inplace.expression
    @classmethod
    def industry(cls):
        return func.trim(cast(cls.properties["industry"], String), '"')

    @hybrid_property
    def status(self) -> str:
        return self.properties.get("status", "active")

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
