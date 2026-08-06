import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from authlib.oauth2.rfc6749 import OAuth2Token

from app.models.identity_provider import IdentityProvider
from app.models.external_identity import ExternalIdentity
from app.models.user import User
from app.models.organization import OrganizationMembership

oauth = OAuth()

async def get_provider_config(db: AsyncSession, provider_id: str) -> IdentityProvider:
    stmt = select(IdentityProvider).where(IdentityProvider.id == provider_id, IdentityProvider.status == 'active')
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Active Identity Provider not found")
    return provider

def create_oauth_client(provider: IdentityProvider) -> StarletteOAuth2App:
    if provider.provider_type != 'oidc':
        raise HTTPException(status_code=400, detail="Not an OIDC provider")
        
    client = oauth.register(
        name=f"oidc_{provider.id}",
        client_id=provider.client_id,
        client_secret=provider.encrypted_client_secret, # TODO: decrypt in a real app
        server_metadata_url=provider.discovery_url,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return client

async def process_sso_login(db: AsyncSession, provider_id: str, user_info: Dict[str, Any]) -> User:
    provider = await get_provider_config(db, provider_id)
    
    email = user_info.get('email')
    subject = user_info.get('sub') or user_info.get('id')
    name = user_info.get('name') or user_info.get('given_name') or "SSO User"
    
    if not subject:
        raise HTTPException(status_code=400, detail="No subject claim returned by provider")

    # 1. Check if ExternalIdentity already exists
    stmt = select(ExternalIdentity).where(
        ExternalIdentity.provider_id == provider.id,
        ExternalIdentity.external_subject == str(subject)
    )
    ext_id = (await db.execute(stmt)).scalar_one_or_none()
    
    if ext_id:
        ext_id.last_authenticated_at = datetime.now(timezone.utc)
        ext_id.external_email = email
        user = (await db.execute(select(User).where(User.id == ext_id.user_id))).scalar_one()
        return user

    # 2. If no ExternalIdentity, check if auto_link is enabled and email matches
    user = None
    if email and provider.auto_link_existing_users:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()

    # 3. If still no user and auto_provision is enabled, create user
    if not user:
        if not provider.auto_provision_users:
            raise HTTPException(status_code=403, detail="Account not found and auto-provisioning is disabled")
            
        if not email:
            # Fallback if no email is provided but provisioning is allowed
            email = f"{subject}@{provider.id}.sso"
            
        user = User(
            full_name=name,
            email=email,
            password_hash="!sso_user", # Unusable password
        )
        db.add(user)
        await db.flush()

    # Create ExternalIdentity link
    new_ext_id = ExternalIdentity(
        organization_id=provider.organization_id,
        user_id=user.id,
        provider_id=provider.id,
        external_subject=str(subject),
        external_email=email,
        last_authenticated_at=datetime.now(timezone.utc)
    )
    db.add(new_ext_id)
    
    # Check org membership
    org_stmt = select(OrganizationMembership).where(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.organization_id == provider.organization_id
    )
    org_member = (await db.execute(org_stmt)).scalar_one_or_none()
    
    if not org_member:
        new_membership = OrganizationMembership(
            user_id=user.id,
            organization_id=provider.organization_id,
            role=provider.default_role or "member"
        )
        db.add(new_membership)
        
    await db.commit()
    return user
