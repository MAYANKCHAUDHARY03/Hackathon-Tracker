import asyncio
import uuid
import logging
from typing import Dict, Any
from sqlalchemy import select

from app.core.event_bus import event_bus
from app.database import AsyncSessionLocal
from app.models.integration import WorkspaceIntegration
from app.services.integration_adapter import IntegrationManager

logger = logging.getLogger(__name__)

async def handle_graph_event(payload: Dict[str, Any]):
    """
    Handles graph-layer events (e.g., project_state_changed, hackathon_launched)
    by dispatching them to active third-party integrations via the Hub.
    """
    workspace_id = payload.get("workspace_id")
    if not workspace_id:
        return
        
    relation_type = payload.get("relation_type")
    
    # We map specific graph edges to actionable events
    action_type = "send_message"
    message_text = f"New graph activity: {payload.get('source_type')} {relation_type} {payload.get('target_type')}"
    
    if relation_type == "REACHED_STATE":
        state = payload.get("properties", {}).get("state", "UNKNOWN")
        message_text = f"Project state transitioned to {state}."
    elif relation_type == "contains" and payload.get("source_type") == "Hackathon" and payload.get("target_type") == "Team":
        message_text = "A new team has joined the hackathon!"

    # Dispatch to all active integrations in the workspace
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WorkspaceIntegration)
            .where(WorkspaceIntegration.workspace_id == uuid.UUID(workspace_id))
            .where(WorkspaceIntegration.is_active == True)
        )
        integrations = result.scalars().all()
        
        for integration in integrations:
            try:
                adapter = IntegrationManager.get_adapter(integration.connector_id, integration.config)
                # Dispatch async so we don't block
                asyncio.create_task(
                    adapter.execute_action(action_type, {"text": message_text, "raw_event": payload})
                )
            except Exception as e:
                logger.error(f"Failed to dispatch to integration {integration.id}: {e}")

def register_integration_dispatcher():
    event_bus.subscribe("graph_edge_created", handle_graph_event)
    logger.info("Integration dispatcher subscribed to graph_edge_created")
