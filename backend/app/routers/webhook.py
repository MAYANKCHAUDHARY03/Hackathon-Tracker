from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database import get_db
from app.dependencies import get_current_user, verify_workspace_access
from app.models.webhook import WebhookSubscription, WebhookDelivery
from app.schemas.webhook import WebhookSubscriptionCreate, WebhookSubscriptionUpdate, WebhookSubscriptionResponse, WebhookDeliveryResponse

router = APIRouter()

@router.post(
    "/workspaces/{workspace_id}/webhooks",
    response_model=WebhookSubscriptionResponse,
    status_code=201
)
async def create_webhook(
    workspace_id: UUID,
    webhook_in: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    
    db_obj = WebhookSubscription(
        workspace_id=workspace_id,
        **webhook_in.model_dump()
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.get(
    "/workspaces/{workspace_id}/webhooks",
    response_model=List[WebhookSubscriptionResponse]
)
async def list_webhooks(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    
    stmt = select(WebhookSubscription).where(WebhookSubscription.workspace_id == workspace_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get(
    "/workspaces/{workspace_id}/webhooks/{webhook_id}/deliveries",
    response_model=List[WebhookDeliveryResponse]
)
async def list_deliveries(
    workspace_id: UUID,
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id=workspace_id, current_user=current_user, db=db)
    
    stmt = select(WebhookDelivery).where(WebhookDelivery.subscription_id == webhook_id).order_by(WebhookDelivery.created_at.desc()).limit(50)
    result = await db.execute(stmt)
    return list(result.scalars().all())
