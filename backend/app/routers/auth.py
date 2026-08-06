import re
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, WorkspaceMembership
from app.models.workspace import Workspace
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import get_password_hash, verify_password, create_access_token
from app.limiter import limiter

router = APIRouter()

def generate_slug(name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-').lower()
    return slug

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(http_request: Request, request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # Create user
        new_user = User(
            full_name=request.full_name,
            email=request.email,
            password_hash=get_password_hash(request.password)
        )
        db.add(new_user)
        await db.flush() # flush to get user ID

        # Create personal workspace
        base_slug = generate_slug(f"{request.full_name} workspace")
        slug = f"{base_slug}-{str(new_user.id)[:8]}"
        
        new_workspace = Workspace(
            name=f"{request.full_name}'s Workspace",
            slug=slug
        )
        db.add(new_workspace)
        await db.flush() # flush to get workspace ID

        # Create membership
        membership = WorkspaceMembership(
            user_id=new_user.id,
            workspace_id=new_workspace.id,
            role="owner"
        )
        db.add(membership)
        
        # Commit transaction
        await db.commit()
        
        # Return token
        access_token = create_access_token(subject=str(new_user.id))
        return TokenResponse(access_token=access_token, token_type="bearer")
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(http_request: Request, request: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token, token_type="bearer")
