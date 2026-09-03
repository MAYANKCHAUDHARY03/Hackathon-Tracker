import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from app.models.user import User
from app.models.organization import Organization, OrganizationMembership
from app.models.organization_trust import OrganizationTrust, TrustStatus
from app.models.federated_identity import FederatedIdentity, FederationStatus
from app.dependencies import verify_organization_access
from fastapi import HTTPException

pytestmark = pytest.mark.asyncio

async def test_federation_boundary_no_trust(db_session: AsyncSession):
    # Setup: User A in Org A trying to access Org B (no trust)
    user = User(id=uuid.uuid4(), email="hacker@orga.com", full_name="Hacker", password_hash="pw", is_active=True)
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

    # Attempt to access Org B
    with pytest.raises(HTTPException) as excinfo:
        await verify_organization_access(organization_id=org_b.id, current_user=user, db=db_session)
    
    assert excinfo.value.status_code == 404
    assert "Organization not found or access denied" in excinfo.value.detail


async def test_federation_boundary_with_trust(db_session: AsyncSession):
    # Setup: User A in Org A, Trust established from Org B -> Org A
    user = User(id=uuid.uuid4(), email="good@orga.com", full_name="Good", password_hash="pw", is_active=True)
    org_a = Organization(id=uuid.uuid4(), name="Org A", slug="org-a-2")
    org_b = Organization(id=uuid.uuid4(), name="Org B", slug="org-b-2")
    
    db_session.add_all([user, org_a, org_b])
    await db_session.flush()
    
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        user_id=user.id,
        role="member",
        status="active"
    )
    trust = OrganizationTrust(
        id=uuid.uuid4(),
        trustor_org_id=org_b.id,
        trustee_org_id=org_a.id,
        status=TrustStatus.ACTIVE,
        allowed_scopes=["federated_reviewer"]
    )
    db_session.add_all([membership, trust])
    await db_session.commit()

    # Attempt to access Org B should succeed and establish FederatedIdentity
    result = await verify_organization_access(organization_id=org_b.id, current_user=user, db=db_session)
    
    assert result["type"] == "federated"
    identity = result["identity"]
    assert identity.target_org_id == org_b.id
    assert identity.home_org_id == org_a.id
    assert "federated_reviewer" in identity.granted_scopes
