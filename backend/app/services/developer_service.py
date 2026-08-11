import secrets
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.developer import DeveloperApp, WebhookEndpoint
from app.schemas.developer import (
    DeveloperAppCreate, DeveloperAppResponse,
    WebhookEndpointCreate, WebhookEndpointResponse
)

class DeveloperService:
    @staticmethod
    async def create_developer_app(
        workspace_id: UUID,
        data: DeveloperAppCreate,
        db: AsyncSession
    ) -> DeveloperAppResponse:
        client_id = f"client_{secrets.token_urlsafe(16)}"
        client_secret = f"secret_{secrets.token_urlsafe(32)}"
        
        app = DeveloperApp(
            workspace_id=workspace_id,
            name=data.name,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uris=data.redirect_uris
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)
        return DeveloperAppResponse.model_validate(app)

    @staticmethod
    async def get_developer_apps(
        workspace_id: UUID,
        db: AsyncSession
    ) -> List[DeveloperAppResponse]:
        query = select(DeveloperApp).where(DeveloperApp.workspace_id == workspace_id)
        result = await db.execute(query)
        apps = result.scalars().all()
        return [DeveloperAppResponse.model_validate(app) for app in apps]

    @staticmethod
    async def create_webhook_endpoint(
        workspace_id: UUID,
        data: WebhookEndpointCreate,
        db: AsyncSession
    ) -> WebhookEndpointResponse:
        webhook_secret = f"whsec_{secrets.token_urlsafe(24)}"
        
        endpoint = WebhookEndpoint(
            workspace_id=workspace_id,
            url=str(data.url),
            events=data.events,
            secret=webhook_secret
        )
        db.add(endpoint)
        await db.commit()
        await db.refresh(endpoint)
        return WebhookEndpointResponse.model_validate(endpoint)

    @staticmethod
    async def get_webhook_endpoints(
        workspace_id: UUID,
        db: AsyncSession
    ) -> List[WebhookEndpointResponse]:
        query = select(WebhookEndpoint).where(WebhookEndpoint.workspace_id == workspace_id)
        result = await db.execute(query)
        endpoints = result.scalars().all()
        return [WebhookEndpointResponse.model_validate(endpoint) for endpoint in endpoints]
