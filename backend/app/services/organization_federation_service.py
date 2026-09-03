import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.organization_trust import OrganizationTrust, TrustStatus
from app.models.federated_identity import FederatedIdentity, FederationStatus

class OrganizationFederationService:
    @staticmethod
    async def create_organization_trust(
        db: AsyncSession,
        trustor_org_id: uuid.UUID,
        trustee_org_id: uuid.UUID,
        allowed_scopes: List[str]
    ) -> OrganizationTrust:
        trust = OrganizationTrust(
            trustor_org_id=trustor_org_id,
            trustee_org_id=trustee_org_id,
            status=TrustStatus.ACTIVE,
            allowed_scopes=allowed_scopes
        )
        db.add(trust)
        await db.commit()
        await db.refresh(trust)
        return trust
        
    @staticmethod
    async def get_trust(
        db: AsyncSession,
        trustor_org_id: uuid.UUID,
        trustee_org_id: uuid.UUID
    ) -> Optional[OrganizationTrust]:
        stmt = select(OrganizationTrust).where(
            OrganizationTrust.trustor_org_id == trustor_org_id,
            OrganizationTrust.trustee_org_id == trustee_org_id,
            OrganizationTrust.status == TrustStatus.ACTIVE
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def establish_federated_identity(
        db: AsyncSession,
        user_id: uuid.UUID,
        home_org_id: uuid.UUID,
        target_org_id: uuid.UUID
    ) -> FederatedIdentity:
        # Check if trust exists
        trust = await OrganizationFederationService.get_trust(db, target_org_id, home_org_id)
        if not trust:
            raise ValueError("No active trust exists between these organizations")
            
        # Check if identity already exists
        stmt = select(FederatedIdentity).where(
            FederatedIdentity.user_id == user_id,
            FederatedIdentity.home_org_id == home_org_id,
            FederatedIdentity.target_org_id == target_org_id
        )
        result = await db.execute(stmt)
        identity = result.scalar_one_or_none()
        
        if identity:
            # Update scopes
            identity.granted_scopes = trust.allowed_scopes
            identity.status = FederationStatus.ACTIVE
        else:
            identity = FederatedIdentity(
                user_id=user_id,
                home_org_id=home_org_id,
                target_org_id=target_org_id,
                status=FederationStatus.ACTIVE,
                granted_scopes=trust.allowed_scopes
            )
            db.add(identity)
            
        await db.commit()
        await db.refresh(identity)
        return identity
