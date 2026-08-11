import uuid
import secrets
import string
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.api_auth import APIKey, OAuthApp
from app.schemas.api_auth import APIKeyCreate, OAuthAppCreate

# Configure passlib to use argon2 (or bcrypt) for hashing secrets
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import hashlib

class APIKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash_key(self, plain_key: str) -> str:
        return hashlib.sha256(plain_key.encode("utf-8")).hexdigest()

    def generate_raw_key(self, prefix: str = "ht_live_") -> tuple[str, str, str]:
        """
        Generates a raw key, its prefix, and its hash.
        Returns: (raw_key, prefix, key_hash)
        """
        random_part = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        raw_key = f"{prefix}{random_part}"
        key_hash = self._hash_key(raw_key)
        return raw_key, prefix, key_hash
        
    def verify_key(self, plain_key: str, key_hash: str) -> bool:
        """Verifies a plain key against a hash"""
        return secrets.compare_digest(self._hash_key(plain_key), key_hash)

    async def create_api_key(
        self, 
        workspace_id: uuid.UUID, 
        user_id: uuid.UUID, 
        data: APIKeyCreate,
        prefix: str = "ht_live_"
    ) -> tuple[APIKey, str]:
        """Creates an API key and returns (APIKey, raw_key)"""
        
        raw_key, prefix, key_hash = self.generate_raw_key(prefix)
        
        api_key = APIKey(
            workspace_id=workspace_id,
            created_by=user_id,
            name=data.name,
            prefix=prefix,
            key_hash=key_hash,
            scopes=data.scopes
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        return api_key, raw_key
        
    async def get_api_key_by_hash(self, key_hash: str) -> APIKey | None:
        stmt = select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_workspace_api_keys(self, workspace_id: uuid.UUID) -> list[APIKey]:
        stmt = select(APIKey).where(APIKey.workspace_id == workspace_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
        
    async def revoke_api_key(self, key_id: uuid.UUID, workspace_id: uuid.UUID) -> APIKey:
        stmt = select(APIKey).where(APIKey.id == key_id, APIKey.workspace_id == workspace_id)
        result = await self.db.execute(stmt)
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="API Key not found")
            
        api_key.is_active = False
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    # For now, placeholder for OAuthApp Service Methods
    def generate_client_credentials(self) -> tuple[str, str, str]:
        client_id = f"client_{secrets.token_hex(12)}"
        client_secret = secrets.token_hex(32)
        client_secret_hash = pwd_context.hash(client_secret)
        return client_id, client_secret, client_secret_hash
        
    async def create_oauth_app(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        data: OAuthAppCreate
    ) -> tuple[OAuthApp, str]:
        client_id, client_secret, client_secret_hash = self.generate_client_credentials()
        
        app = OAuthApp(
            workspace_id=workspace_id,
            created_by=user_id,
            name=data.name,
            description=data.description,
            homepage_url=data.homepage_url,
            callback_urls=data.callback_urls,
            client_id=client_id,
            client_secret_hash=client_secret_hash
        )
        
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        
        return app, client_secret
