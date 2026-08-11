import hashlib
import uuid
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.api_auth import APIKey

# We can accept the API key in the X-API-Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def _hash_key(plain_key: str) -> str:
    return hashlib.sha256(plain_key.encode("utf-8")).hexdigest()

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """
    Dependency that validates the provided API key and returns the APIKey object.
    Requires the API key to be passed in the X-API-Key header.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key header",
        )
        
    key_hash = _hash_key(api_key_header)
    
    stmt = select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API Key",
        )
        
    return api_key

def require_scopes(required_scopes: list[str]):
    """
    Dependency generator to require specific scopes for an API endpoint.
    Example usage:
    @router.get("/something", dependencies=[Depends(require_scopes(["projects:read"]))])
    """
    async def scope_checker(api_key: APIKey = Depends(get_api_key)):
        for scope in required_scopes:
            if scope not in api_key.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Missing scope: {scope}",
                )
        return api_key
        
    return scope_checker
