from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.models.integration import WorkspaceIntegration
from app.schemas.hub_integration import WorkspaceIntegrationCreate, WorkspaceIntegrationResponse, WorkspaceIntegrationUpdate, ConnectorInfo
from app.services.integration_adapter import IntegrationManager

router = APIRouter(prefix="/hub-integrations", tags=["Enterprise Integration Hub"])

AVAILABLE_CONNECTORS = [
    {
        "id": "slack",
        "name": "Slack",
        "category": "Communication",
        "description": "Send notifications and updates to Slack channels.",
        "auth_type": "webhook",
        "config_schema": {
            "fields": [
                {"id": "webhook_url", "label": "Webhook URL", "type": "text", "required": True}
            ]
        }
    },
    {
        "id": "jira",
        "name": "Jira Software",
        "category": "Issue Tracking",
        "description": "Create issues and sync statuses with Jira.",
        "auth_type": "api_key",
        "config_schema": {
            "fields": [
                {"id": "domain", "label": "Jira Domain (e.g., https://your-domain.atlassian.net)", "type": "text", "required": True},
                {"id": "api_key", "label": "API Token", "type": "text", "required": True},
                {"id": "email", "label": "Admin Email", "type": "text", "required": True}
            ]
        }
    }
]

@router.get("/connectors", response_model=List[ConnectorInfo])
async def list_connectors():
    return AVAILABLE_CONNECTORS

@router.get("/workspaces/{workspace_id}", response_model=List[WorkspaceIntegrationResponse])
async def list_workspace_integrations(workspace_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkspaceIntegration).where(WorkspaceIntegration.workspace_id == workspace_id)
    )
    return result.scalars().all()

@router.post("/", response_model=WorkspaceIntegrationResponse)
async def create_integration(data: WorkspaceIntegrationCreate, db: AsyncSession = Depends(get_db)):
    integration = WorkspaceIntegration(
        workspace_id=data.workspace_id,
        connector_id=data.connector_id,
        name=data.name,
        is_active=data.is_active,
        config=data.config
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration

@router.post("/{integration_id}/test")
async def test_integration(integration_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkspaceIntegration).where(WorkspaceIntegration.id == integration_id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    try:
        adapter = IntegrationManager.get_adapter(integration.connector_id, integration.config)
        success = await adapter.test_connection()
        if success:
            integration.last_sync_status = "success"
            integration.last_sync_error = None
        else:
            integration.last_sync_status = "error"
            integration.last_sync_error = "Connection test failed."
    except Exception as e:
        integration.last_sync_status = "error"
        integration.last_sync_error = str(e)
        
    await db.commit()
    return {"status": integration.last_sync_status, "error": integration.last_sync_error}
