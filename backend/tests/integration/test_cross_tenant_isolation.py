import pytest
from httpx import AsyncClient
import uuid
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

pytestmark = pytest.mark.asyncio

async def test_cross_tenant_api_isolation(async_client: AsyncClient, db_session: AsyncSession):
    # Setup
    user = User(id=uuid.uuid4(), email="cross@tenant.com", full_name="Cross", password_hash="pw", is_active=True)
    org_a = Organization(id=uuid.uuid4(), name="Org A", slug="org-a")
    org_b = Organization(id=uuid.uuid4(), name="Org B", slug="org-b")
    
    db_session.add_all([user, org_a, org_b])
    await db_session.flush()
    
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        user_id=user.id,
        role="member",
        status="active"
    )
    db_session.add(membership)
    await db_session.commit()
    
    # Login as User (Need a valid token - mocking or generating one)
    from app.config import settings
    from jose import jwt
    token = jwt.encode({"sub": str(user.id)}, settings.SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Attempt to hit an org-specific endpoint for org A (should succeed if endpoint exists, but let's just use federation trust endpoint which requires verify_organization_access)
    # The trusts endpoint is GET /api/v1/organizations/{organization_id}/federation/trusts
    response_a = await async_client.get(f"/api/v1/organizations/{org_a.id}/federation/trusts", headers=headers)
    
    # Assuming endpoint exists and user has access (might be 403 if they are not admin, but let's check it's not 404 access denied)
    # Actually wait, federation trusts might require admin. Let's just check the response is not 404 for Org A, but 404 for Org B
    assert response_a.status_code in [200, 403]
    
    # Attempt to hit an org-specific endpoint for org B (should return 404 as per our dependency)
    response_b = await async_client.get(f"/api/v1/organizations/{org_b.id}/federation/trusts", headers=headers)
    assert response_b.status_code == 404
    assert response_b.json()["detail"] == "Organization not found or access denied"
