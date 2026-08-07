from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import WorkspaceMembership
from app.models.automation import AutomationRule, AutomationExecution
from app.dependencies import verify_workspace_access, require_workspace_admin
from app.schemas.automation import (
    AutomationRuleCreate,
    AutomationRuleUpdate,
    AutomationRuleResponse,
    AutomationExecutionResponse
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/automation",
    tags=["automation"]
)

@router.get("/rules", response_model=List[AutomationRuleResponse])
async def list_automation_rules(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """List all automation rules for a workspace."""
    query = select(AutomationRule).where(
        AutomationRule.workspace_id == workspace_id,
        AutomationRule.archived_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(
    workspace_id: UUID,
    rule_in: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Create a new automation rule (requires workspace admin)."""
    # Force the workspace_id from path
    rule_in.workspace_id = workspace_id
    
    from app.models.organization import Workspace
    ws_query = select(Workspace).where(Workspace.id == workspace_id)
    ws_result = await db.execute(ws_query)
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    rule_in.organization_id = workspace.organization_id
    db_rule = AutomationRule(**rule_in.model_dump(), created_by=membership.user_id)
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule

@router.get("/rules/{rule_id}", response_model=AutomationRuleResponse)
async def get_automation_rule(
    workspace_id: UUID,
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """Get specific automation rule."""
    query = select(AutomationRule).where(
        AutomationRule.id == rule_id,
        AutomationRule.workspace_id == workspace_id,
        AutomationRule.archived_at.is_(None)
    )
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=AutomationRuleResponse)
async def update_automation_rule(
    workspace_id: UUID,
    rule_id: UUID,
    rule_in: AutomationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Update automation rule (requires workspace admin)."""
    query = select(AutomationRule).where(
        AutomationRule.id == rule_id,
        AutomationRule.workspace_id == workspace_id,
        AutomationRule.archived_at.is_(None)
    )
    result = await db.execute(query)
    db_rule = result.scalar_one_or_none()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
        
    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rule, field, value)
        
    db_rule.updated_by = membership.user_id
    await db.commit()
    await db.refresh(db_rule)
    return db_rule

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation_rule(
    workspace_id: UUID,
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(require_workspace_admin)
):
    """Delete (archive) automation rule."""
    from datetime import datetime, timezone
    
    query = select(AutomationRule).where(
        AutomationRule.id == rule_id,
        AutomationRule.workspace_id == workspace_id,
        AutomationRule.archived_at.is_(None)
    )
    result = await db.execute(query)
    db_rule = result.scalar_one_or_none()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
        
    db_rule.archived_at = datetime.now(timezone.utc)
    db_rule.updated_by = membership.user_id
    await db.commit()
    return None

@router.get("/rules/{rule_id}/executions", response_model=List[AutomationExecutionResponse])
async def list_rule_executions(
    workspace_id: UUID,
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMembership = Depends(verify_workspace_access)
):
    """List executions for a specific rule."""
    # First verify rule belongs to workspace
    rule_query = select(AutomationRule).where(
        AutomationRule.id == rule_id,
        AutomationRule.workspace_id == workspace_id
    )
    rule_result = await db.execute(rule_query)
    if not rule_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Automation rule not found in workspace")
        
    exec_query = select(AutomationExecution).where(
        AutomationExecution.rule_id == rule_id
    ).order_by(AutomationExecution.created_at.desc()).limit(100)
    
    result = await db.execute(exec_query)
    return result.scalars().all()
