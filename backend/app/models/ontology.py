import uuid
import enum
from sqlalchemy import Column, String, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseEntity

class EntityType(str, enum.Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    COMMUNITY = "community"
    PROGRAM = "program"
    HACKATHON = "hackathon"
    CHALLENGE = "challenge"
    PROBLEM = "problem"
    IDEA = "idea"
    TEAM = "team"
    PROJECT = "project"
    TECHNOLOGY = "technology"
    SKILL = "skill"
    MENTOR = "mentor"
    JUDGE = "judge"
    SPONSOR = "sponsor"
    RESEARCH = "research"
    DATASET = "dataset"
    STARTUP = "startup"
    PRODUCT = "product"
    PILOT = "pilot"
    OPPORTUNITY = "opportunity"
    ACHIEVEMENT = "achievement"
    IMPACT = "impact"

class VerificationLevel(str, enum.Enum):
    UNVERIFIED = "unverified"
    SELF_DECLARED = "self_declared"
    PLATFORM_VERIFIED = "platform_verified"
    ORGANIZATION_VERIFIED = "organization_verified"
    MULTI_SOURCE_VERIFIED = "multi_source_verified"

class VisibilityLevel(str, enum.Enum):
    PRIVATE = "private"
    CONNECTION_ONLY = "connection_only"
    SELECTIVE_SHARING = "selective_sharing"
    PUBLIC = "public"

class UniversalEntity(BaseEntity):
    __tablename__ = "ontology_entities"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(SQLEnum(EntityType), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    source = Column(String(100), nullable=False, default="user-provided")
    verification_level = Column(SQLEnum(VerificationLevel), nullable=False, default=VerificationLevel.UNVERIFIED)
    visibility = Column(SQLEnum(VisibilityLevel), nullable=False, default=VisibilityLevel.PRIVATE)
    
    properties = Column(JSON, nullable=False, default=dict)

    __mapper_args__ = {
        "polymorphic_on": entity_type,
        "polymorphic_identity": "universal"
    }
