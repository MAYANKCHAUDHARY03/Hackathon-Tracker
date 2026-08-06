# Stage 3: SAML Enterprise SSO

## Implementation Summary
- **SAML Service**: Created `saml_service.py` leveraging `python3-saml` and `xmlsec` to process SAML Assertions and authenticate users securely via POST.
- **Dynamic Configuration**: Added `get_saml_settings` that dynamically translates `IdentityProvider` metadata (Entity ID, Certificate, SSO URL) into the configuration required by `python3-saml`.
- **SAML Endpoints**: Added `/saml/login/{provider_id}` for SP-initiated SSO redirection (HTTP-Redirect binding) and `/saml/acs/{provider_id}` for processing IdP responses (HTTP-POST binding).
- **Security Check**: Enforced `strict=True` mode, which validates audience, recipient, issuer, time-conditions, and requires signed assertions.

Stage 3 complete. Proceeding to SCIM Provisioning.
