from fastapi import Request, HTTPException
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Tuple

from app.models.identity_provider import IdentityProvider
from app.services.sso_service import get_provider_config, process_sso_login

async def prepare_saml_request(request: Request) -> Dict[str, Any]:
    # Need to convert FastAPI Request to python3-saml Request dict
    url_data = request.url
    return {
        'https': 'on' if url_data.scheme == 'https' else 'off',
        'http_host': url_data.netloc,
        'server_port': url_data.port,
        'script_name': request.url.path,
        'get_data': dict(request.query_params),
        'post_data': dict((await request.form())),
        'lowercase_urlencoding': False
    }

def get_saml_settings(provider: IdentityProvider) -> OneLogin_Saml2_Settings:
    if provider.provider_type != 'saml':
        raise HTTPException(status_code=400, detail="Not a SAML provider")
        
    settings = {
        "strict": True,
        "debug": False,
        "sp": {
            "entityId": "hackathon-tracker-sp",
            "assertionConsumerService": {
                "url": "", # Replaced dynamically based on request
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
        },
        "idp": {
            "entityId": provider.issuer,
            "singleSignOnService": {
                "url": provider.metadata_url, # Usually login url is provided here
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": provider.certificate_reference
        }
    }
    
    return OneLogin_Saml2_Settings(settings)

async def init_saml_auth(request: Request, provider: IdentityProvider) -> OneLogin_Saml2_Auth:
    req = await prepare_saml_request(request)
    settings = get_saml_settings(provider)
    settings.set_sp_acs_url(str(request.url_for("saml_acs", provider_id=provider.id)))
    auth = OneLogin_Saml2_Auth(req, settings.get_settings_data())
    return auth

async def process_saml_callback(db: AsyncSession, request: Request, provider_id: str) -> Any:
    provider = await get_provider_config(db, provider_id)
    auth = await init_saml_auth(request, provider)
    
    auth.process_response()
    
    errors = auth.get_errors()
    if errors:
        raise HTTPException(status_code=401, detail=f"SAML Validation Error: {', '.join(errors)}")
        
    if not auth.is_authenticated():
        raise HTTPException(status_code=401, detail="SAML Authentication Failed")

    # NameID is usually the subject
    subject = auth.get_nameid()
    attributes = auth.get_attributes()
    
    # Simple attribute mapping
    email = attributes.get('email', [None])[0] or attributes.get('mail', [None])[0]
    name = attributes.get('displayName', [None])[0] or attributes.get('givenName', [None])[0] or subject

    user_info = {
        'sub': subject,
        'email': email,
        'name': name
    }
    
    return await process_sso_login(db, provider_id, user_info)
