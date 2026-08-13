from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
import uuid
import re

# Defined Canonical Event Types for Phase 47
class EventType:
    PROJECT_CREATED = "project_created"
    TASK_COMPLETED = "task_completed"
    CHALLENGE_CREATED = "challenge_created"
    TEAM_JOINED = "team_joined"
    SUBMISSION_CREATED = "submission_created"
    EVALUATION_COMPLETED = "evaluation_completed"
    AWARD_VERIFIED = "award_verified"
    PROJECT_DEPLOYED = "project_deployed"
    # General fallbacks or other modules
    GENERAL_ACTIVITY = "general_activity"
    AUDIT_LOG = "audit_log"

class EventBase(BaseModel):
    workspace_id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    entity_type: str
    entity_id: Optional[str] = None
    event_type: str
    source: str = "api"
    correlation_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

    @field_validator("metadata_json")
    @classmethod
    def sanitize_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not v:
            return v
        sensitive_keys = re.compile(r"(password|token|secret|key|auth|credential|ssn|credit_card)", re.IGNORECASE)
        sanitized = {}
        for key, value in v.items():
            if sensitive_keys.search(key):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: uuid.UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
