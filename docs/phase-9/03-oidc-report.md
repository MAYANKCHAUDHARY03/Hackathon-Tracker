# Stage 2: OIDC Enterprise SSO

## Implementation Summary
- **SSO Service**: Created `sso_service.py` to instantiate `Authlib` OAuth2 clients dynamically based on `IdentityProvider` configurations from the database.
- **SSO Router**: Added `/api/v1/auth/sso/login/{provider_id}` and `/api/v1/auth/sso/callback/{provider_id}` endpoints.
- **Session Support**: Integrated Starlette's `SessionMiddleware` into FastAPI app to manage OAuth state and nonces.
- **Account Provisioning**: The callback flow checks `auto_link_existing_users` and `auto_provision_users`. It provisions users in the database and automatically assigns them to the appropriate organization with the default role if enabled.
- **Security Features**: Rate limiting applies to SSO initialization (5/minute) just like standard registration.

Stage 2 complete. Proceeding to SAML integration.
