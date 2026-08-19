from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
import uuid

class InnovationObjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Unique identifier for the object across the ecosystem")
    type: str = Field(description="The concrete type of the innovation object")
    source: str = Field(description="The origin system/institution of this object")
    owner: str = Field(description="The owner identifier of this object")
    version: str = Field(default="1.0", description="Schema version of this object")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp")
    verification: Dict[str, Any] = Field(default_factory=dict, description="Cryptographic or systemic verification signatures/claims")
    visibility: str = Field(default="public", description="public, private, or protected")
    relationships: Dict[str, List[str]] = Field(default_factory=dict, description="References to other innovation objects")

class InnovationEvent(InnovationObjectBase):
    type: Literal["InnovationEvent"] = "InnovationEvent"
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str

class InnovationProject(InnovationObjectBase):
    type: Literal["InnovationProject"] = "InnovationProject"
    title: str
    summary: Optional[str] = None
    repository_url: Optional[str] = None
    status: str

class InnovationChallenge(InnovationObjectBase):
    type: Literal["InnovationChallenge"] = "InnovationChallenge"
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None

class InnovationAchievement(InnovationObjectBase):
    type: Literal["InnovationAchievement"] = "InnovationAchievement"
    title: str
    issued_at: datetime
    evidence_url: Optional[str] = None

class InnovationOrganization(InnovationObjectBase):
    type: Literal["InnovationOrganization"] = "InnovationOrganization"
    name: str
    domain: Optional[str] = None

class InnovationPerson(InnovationObjectBase):
    type: Literal["InnovationPerson"] = "InnovationPerson"
    name: str
    email_hash: Optional[str] = None
    skills: List[str] = []

class InnovationProgram(InnovationObjectBase):
    type: Literal["InnovationProgram"] = "InnovationProgram"
    name: str
    description: Optional[str] = None
    program_type: str

InnovationObject = Union[
    InnovationEvent,
    InnovationProject,
    InnovationChallenge,
    InnovationAchievement,
    InnovationOrganization,
    InnovationPerson,
    InnovationProgram
]

class InnovationProtocolExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    version: str = "1.0"
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    source_system: str
    objects: List[InnovationObject]
