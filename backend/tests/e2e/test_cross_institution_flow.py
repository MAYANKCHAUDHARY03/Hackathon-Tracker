import pytest
from httpx import AsyncClient
import uuid
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership
from app.models.organization_trust import OrganizationTrust, TrustStatus
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

async def test_cross_institution_e2e_flow(async_client: AsyncClient, db_session: AsyncSession):
    # Setup
    user = User(id=uuid.uuid4(), email="student@university.edu", full_name="Student", password_hash="pw", is_active=True)
    org_university = Organization(id=uuid.uuid4(), name="University", slug="university")
    org_enterprise = Organization(id=uuid.uuid4(), name="Enterprise", slug="enterprise")
    
    db_session.add_all([user, org_university, org_enterprise])
    await db_session.flush()
    
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        organization_id=org_university.id,
        user_id=user.id,
        role="member",
        status="active"
    )
    trust = OrganizationTrust(
        id=uuid.uuid4(),
        trustor_org_id=org_enterprise.id,
        trustee_org_id=org_university.id,
        status=TrustStatus.ACTIVE,
        allowed_scopes=["federated_reviewer"]
    )
    db_session.add_all([membership, trust])
    await db_session.commit()
    
    # Login
    from app.config import settings
    from jose import jwt
    token = jwt.encode({"sub": str(user.id)}, settings.SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Target endpoint in Enterprise Org
    # Even if we don't have many routes, /api/v1/organizations/{organization_id}/federation/trusts uses the dependency
    response = await async_client.get(f"/api/v1/organizations/{org_enterprise.id}/federation/trusts", headers=headers)
    
    # As a federated user, they should not get 404 access denied. 
    # They might get 403 because they aren't admin, or 200 depending on the endpoint logic.
    assert response.status_code in [200, 403]
    
    # Let's check that the federated identity was created
    from app.models.federated_identity import FederatedIdentity
    from sqlalchemy import select
    
    stmt = select(FederatedIdentity).where(
        FederatedIdentity.user_id == user.id,
        FederatedIdentity.target_org_id == org_enterprise.id
    )
    res = await db_session.execute(stmt)
    fed_id = res.scalar_one_or_none()
    
    assert fed_id is not None
    assert fed_id.home_org_id == org_university.id
    assert "federated_reviewer" in fed_id.granted_scopes
