# Phase 66: Identity and Federation Audits

## 1. Architecture Audit
The current system architecture separates multitenancy into two levels:
1. **Organizations:** Top-level multi-tenant boundaries (`Organization` model).
2. **Workspaces:** Isolated collaboration areas within or outside an organization (`Workspace` model).

Identity and multi-tenancy are structured around `OrganizationMembership` and `WorkspaceMembership`. The system supports external federation at the workspace level (`WorkspaceFederation`) and organizational trust (`OrganizationTrust`).

## 2. Identity Model Audit
Users are represented by the `User` model containing basic identity (email, password_hash, github, linkedin). 
Identities currently interact via:
- `WorkspaceMembership` (role-based association to workspaces)
- `OrganizationMembership` (role-based association to organizations)
- `PortableIdentity` (abstracting user achievements/history across organizations)

## 3. Tenant Isolation Audit
Tenant isolation guarantees are currently enforced at the database level using `organization_id` and `workspace_id` foreign keys. Data access requires active membership.
- The `api_auth.py` models (`OAuthApp` and `APIKey`) are tightly coupled to `workspace_id`, restricting programmatic access.
- Cross-tenant leakage is prevented primarily through application-level checks in the repository and service layers verifying `user_id` in the respective `memberships` tables.

## 4. RBAC Audit
Role-based access control is implemented via a string `role` field in both `WorkspaceMembership` (e.g., "member") and `OrganizationMembership`. 
Current implementation:
- Relies on application-side logic mapping roles to permissions.
- Hardcoded roles like "admin", "member", "reviewer".
- Trust relationships (`OrganizationTrust`) introduce `allowed_scopes` which limit federated user access, but it's not fully integrated into a dynamic RBAC engine.
