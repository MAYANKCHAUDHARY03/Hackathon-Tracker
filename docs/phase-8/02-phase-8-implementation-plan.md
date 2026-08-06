# Phase 8 Implementation Plan

## Goal Description
Transform Hackathon Tracker from a workspace-centric application into an organisation-ready multi-workspace platform. This involves introducing an `Organization` model, defining organisation memberships and role-based capabilities, grouping workspaces under organisations, and maintaining full audit trails (governance). This phase brings enterprise-level administration without breaking existing standalone workspace functionality.

## Proposed Changes

### 1. Organization Domain (Stage 1)
- Create `Organization`, `OrganizationMembership`, and `OrganizationSettings` models.
- **Migration Strategy:** Provide an Alembic migration that sets up the tables. For existing workspaces without organisations, we will associate them with a safe default "Legacy Organization" or leave them unassociated if the architecture permits unassociated workspaces initially. The prompt specifies: "workspace belongs to zero or one organisation during migration".
- Define the new relationship in `Workspace` (`organization_id`).

### 2. Role and Capability System (Stage 2)
- Implement a capability abstraction. Roles (`owner`, `admin`, `security_admin`, `auditor`, `workspace_manager`, `member`) will map to granular capabilities (e.g. `organization.view`, `workspace.manage`).
- Implement scoped permission checks within the backend to ensure a user acts within the intersection of their organisation role and their specific workspace role (e.g., a `workspace_manager` only has rights over assigned workspaces).

### 3. Organization Admin APIs (Stage 3)
- Create `/api/v1/organizations` routes for CRUD.
- Add `/api/v1/organizations/{id}/members` for user lifecycle management.
- Add summary APIs `/api/v1/organizations/{id}/summary` to return aggregate statistics.

### 4. Session & Access Lifecycle (Stage 4)
- Introduce a mechanism to revoke sessions or access tokens. Given the current JWT implementation, if stateless, we will introduce a `TokenBlocklist` or a `session_version` counter on the `User` model. Incrementing `session_version` invalidates all previously issued JWTs.
- Enforce revocation upon suspension, removal, or role degradation.

### 5. Audit Logging (Stage 5)
- Implement an `AuditEvent` model to record actions (CRUD operations on organizations, workspace creation, membership changes).
- Hook critical backend routes (e.g., auth, organization mutation, security policies) to automatically create an append-only log in the database.
- Create `/api/v1/organizations/{id}/audit` endpoints with CSV/JSON exports.

### 6. Enterprise Analytics (Stage 6)
- Build aggregate queries on workspaces and hackathons grouped by organisation.
- Create `/api/v1/organizations/{id}/analytics` to provide data for the frontend dashboards.

### 7. Frontend Integration (Stage 7)
- Introduce Organization-level dashboards.
- Add new administration views (Member Management, Workspace Management, Security Settings, Audit Explorer).
- Ensure existing navigation smoothly accommodates both organisation administration and individual workspace interaction.

## Verification Plan
1. **End-to-End Enterprise Flow:** Log in as an Organization Owner, verify abilities to create workspaces and invite users.
2. **Access Revocation:** Suspend a user and verify immediate API rejection (`401/403`).
3. **Data Isolation:** Create multiple organizations and ensure users cannot access or view workspaces from unassigned organizations.
4. **Audit Integrity:** Export an audit log and verify it includes timestamps, actor user IDs, and no sensitive credentials.
5. **No Regressions:** Verify the base application remains functionally intact (Hackathons, Projects, Kanban boards work properly).
