from pydantic import BaseModel
from typing import List, Dict, Any

class WorkspaceExport(BaseModel):
    version: str = "1.0"
    workspace: Dict[str, Any]
    hackathons: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]

class ImportPreviewResponse(BaseModel):
    is_valid: bool
    hackathons_count: int
    projects_count: int
    teams_count: int
    errors: List[str]

class ImportExecuteRequest(BaseModel):
    data: WorkspaceExport
    overwrite: bool = False
