from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.database import get_db
from app.services.sso_service import create_oauth_client, get_provider_config, process_sso_login
from app.services.auth_service import create_access_token
from app.limiter import limiter

router = APIRouter()

@router.get("/login/{provider_id}")
@limiter.limit("5/minute")
async def sso_login(request: Request, provider_id: str, db: AsyncSession = Depends(get_db)):
    provider = await get_provider_config(db, provider_id)
    client = create_oauth_client(provider)
    redirect_uri = request.url_for("sso_callback", provider_id=provider_id)
    return await client.authorize_redirect(request, str(redirect_uri))

@router.get("/callback/{provider_id}")
async def sso_callback(request: Request, provider_id: str, db: AsyncSession = Depends(get_db)):
    try:
        provider = await get_provider_config(db, provider_id)
        client = create_oauth_client(provider)
        token = await client.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        if not user_info:
            user_info = await client.userinfo(token=token)

        user = await process_sso_login(db, provider_id, user_info)
        access_token = create_access_token(subject=str(user.id))
        
        # Return to frontend with token in fragment or query
        # Usually frontend expects a redirect to /sso/success#token=...
        return RedirectResponse(url=f"/sso/success#token={access_token}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return RedirectResponse(url=f"/login?error=sso_failed")

from app.services.saml_service import init_saml_auth, process_saml_callback
@router.get('/saml/login/{provider_id}')
@limiter.limit('5/minute')
async def saml_login(request: Request, provider_id: str, db: AsyncSession = Depends(get_db)):
    provider = await get_provider_config(db, provider_id)
    auth = await init_saml_auth(request, provider)
    sso_built_url = auth.login()
    return RedirectResponse(url=sso_built_url)

@router.post('/saml/acs/{provider_id}')
async def saml_acs(request: Request, provider_id: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await process_saml_callback(db, request, provider_id)
        access_token = create_access_token(subject=str(user.id))
        return RedirectResponse(url=f'/sso/success#token={access_token}', status_code=303)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return RedirectResponse(url='/login?error=saml_failed', status_code=303)

