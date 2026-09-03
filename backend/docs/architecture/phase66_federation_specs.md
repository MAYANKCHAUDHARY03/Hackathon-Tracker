# Phase 66: Federation Specifications

## Step 5: Permission Model Spec

The dynamic RBAC evaluation required for federated users intersects with `allowed_scopes` in `OrganizationTrust` as follows:

1.  **Base Role Assignment**: A user receives a base role within their home organization or workspace (e.g., `WORKSPACE_MEMBER`, `ORG_ADMIN`).
2.  **Federation Context**: When a user attempts to access resources in a target organization (the "Resource Org") using an identity from a source organization (the "Identity Org"), the system evaluates the `OrganizationTrust` record between the two orgs.
3.  **Scope Intersection**: The user's effective permissions in the Resource Org are strictly bounded by the intersection of:
    *   The permissions granted by their base role in the Identity Org (or specific federated grants).
    *   The `allowed_scopes` defined in the `OrganizationTrust` by the Resource Org.
4.  **Tenant Isolation Boundary**: By default, no access is granted. The trust must explicitly whitelist scopes (e.g., `projects:read`, `evaluations:write`).

## Step 6: Federation Protocol Spec

The flow for organization verification, delegated access, and scoped federation permissions:

1.  **Trust Establishment**:
    *   Org A (Resource Org) creates an `OrganizationTrust` pointing to Org B (Identity Org).
    *   Org A configures `allowed_scopes` (e.g., allowing Org B users to view public projects).
    *   (Optional) Mutual trust requires Org B to create a reciprocal `OrganizationTrust`.
2.  **Federated Access Token Issuance**:
    *   A user from Org B requests a federated access token for Org A.
    *   The system validates the user's active session in Org B.
    *   The system checks the active `OrganizationTrust` from Org A to Org B.
    *   A scoped JWT is issued containing the `federation_target: org_A_id` and the intersected scopes.
3.  **API Authorization**:
    *   The API Gateway / Auth Dependency inspects the token.
    *   If `federation_target` is present, it routes the authorization check through the `FederationService`, which validates that the requested resource belongs to `federation_target` and the action is within the token's scopes.
