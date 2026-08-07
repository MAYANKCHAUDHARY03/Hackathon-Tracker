from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import uuid

from app.models.automation import AutomationRule, AutomationExecution

logger = logging.getLogger(__name__)

class AutomationService:
    @staticmethod
    async def process_event(
        db: AsyncSession,
        workspace_id: UUID,
        trigger_type: str,
        event_data: Dict[str, Any]
    ) -> List[AutomationExecution]:
        """
        Process an event and execute any matching automation rules.
        """
        # Find active rules matching this trigger in the workspace
        query = select(AutomationRule).where(
            AutomationRule.workspace_id == workspace_id,
            AutomationRule.trigger_type == trigger_type,
            AutomationRule.enabled == True,
            AutomationRule.archived_at.is_(None)
        )
        
        result = await db.execute(query)
        rules = result.scalars().all()
        
        executions = []
        for rule in rules:
            if AutomationService._evaluate_conditions(rule.conditions, event_data):
                execution = await AutomationService._execute_rule(db, rule, event_data)
                executions.append(execution)
                
        return executions

    @staticmethod
    def _evaluate_conditions(conditions: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """
        Evaluate if event_data matches the rule conditions.
        Format: {"field": "status", "operator": "equals", "value": "completed"}
        """
        if not conditions:
            return True
            
        # Simplified condition evaluator
        field = conditions.get("field")
        operator = conditions.get("operator")
        value = conditions.get("value")
        
        if not field or field not in event_data:
            return False
            
        actual_value = event_data.get(field)
        
        if operator == "equals":
            return actual_value == value
        elif operator == "contains" and isinstance(actual_value, str):
            return value in actual_value
        elif operator == "exists":
            return actual_value is not None
            
        return False

    @staticmethod
    async def _execute_rule(
        db: AsyncSession, 
        rule: AutomationRule, 
        event_data: Dict[str, Any]
    ) -> AutomationExecution:
        """
        Record execution and apply action (idempotent design).
        """
        execution = AutomationExecution(
            rule_id=rule.id,
            triggering_event=event_data,
            status="running",
            attempts=1,
            started_at=datetime.now(timezone.utc),
            correlation_id=str(uuid.uuid4())
        )
        
        db.add(execution)
        # Flush to get ID
        await db.flush()
        
        try:
            # Perform action based on rule.action_type
            if rule.action_type == "send_notification":
                from app.models.notification import Notification
                notif = Notification(
                    workspace_id=rule.workspace_id,
                    user_id=rule.created_by,
                    title=f"Automation: {rule.name}",
                    content=f"Triggered by {rule.trigger_type}",
                    type="automation"
                )
                db.add(notif)
            elif rule.action_type == "ai_evaluate_submission":
                from app.models.activity import Activity
                from app.services.ai.providers import AIProviderFactory
                from app.config import settings
                
                provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else AIProviderFactory.get_provider("mock", "dummy")
                summary = await provider.generate_project_summary({"event": event_data, "rule": rule.name})
                
                act = Activity(
                    workspace_id=rule.workspace_id,
                    action="ai_evaluation",
                    entity_type="submission",
                    entity_id=event_data.get("submission_id") or rule.id,
                    details={"ai_summary": summary}
                )
                db.add(act)
            elif rule.action_type == "assign_evaluator":
                pass
            else:
                raise ValueError(f"Unknown action type: {rule.action_type}")
                
            execution.status = "completed"
            
        except Exception as e:
            logger.error(f"Rule execution failed: {e}")
            execution.status = "failed"
            execution.error = str(e)
            
        execution.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(execution)
        
        return execution
