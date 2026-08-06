# Stage 1: Provider-Neutral Identity Architecture

## Implementation Summary
- **Created `IdentityProvider` model**: Contains fields for provider configuration (OIDC/SAML), credentials (encrypted), discovery URLs, domains, and provisioning rules.
- **Created `ExternalIdentity` model**: Links a `User` to an `IdentityProvider` with a unique `external_subject`.
- **Database Migrations**: Generated and applied migration to create `identity_providers` and `external_identities` tables.

## Testing & Verification
- Validated constraints such as `uq_provider_subject` on the external identities.
- Verified that deleting an organization cascades to its identity providers and identities (enforced via `ondelete="CASCADE"`).
- Checked that SQLAlchemy loads models properly.

Stage 1 complete. Ready to proceed to OIDC integration.
