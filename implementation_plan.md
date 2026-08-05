# Phase 3 Prompt 2 Implementation Plan: Workspace Invitation Flow

## Goal Description
Implement the Workspace Invitation Flow and Workspace Switching. This allows workspace owners to invite users via email, users to accept invitations and join workspaces, and users to switch between multiple active workspaces they belong to.

## Proposed Changes

### Backend Components

#### [MODIFY] app/schemas/workspace.py
- Add `WorkspaceInvitationCreate` schema for incoming API requests (email, workspace_role).
- Add `WorkspaceInvitationResponse` schema to serialize invitation data to clients.

#### [NEW] app/routers/invitations.py
- Create a new router for invitations.
- `POST /api/v1/workspaces/{workspace_id}/invitations`: Create an invitation (requires workspace owner/admin role).
- `GET /api/v1/workspaces/{workspace_id}/invitations`: List pending invitations.
- `POST /api/v1/workspaces/{workspace_id}/invitations/{invitation_id}/revoke`: Revoke an invitation.
- `POST /api/v1/invitations/accept`: Accept an invitation using the unique token (unauthenticated or authenticated? Must be authenticated to join, or we require them to log in first and pass the token).

#### [MODIFY] app/main.py
- Include the new `invitations` router.

#### [NEW] tests/test_invitations.py
- Add automated tests to verify creation, listing, revoking, and accepting of invitations.

### Frontend Components

#### [MODIFY] src/store/workspaceStore.ts
- Introduce `activeWorkspaceId` state to track the currently selected workspace.
- Actions to `setActiveWorkspace` and persist it (e.g., in localStorage).
- Automatically select a default workspace upon fetching if none is selected.

#### [MODIFY] src/components/layout/Topbar.tsx & Sidebar.tsx
- Add a dropdown or select input to allow the user to switch their active workspace.

#### [NEW] src/features/workspaces/components/InvitationManager.tsx
- UI component to list pending invitations and invite new users by email.
- Embed this inside the Workspace Settings or Dashboard.

#### [NEW] src/pages/AcceptInvitation.tsx
- A new route `/invitations/accept?token=...` that handles taking the token from the URL, verifying it, and calling the accept API.
- If the user is unauthenticated, redirect them to login/register with a redirect URI back to the accept invitation page.

## Verification Plan

### Automated Tests
- Run `pytest tests/test_invitations.py -v` to ensure backend invitation logic handles token generation, uniqueness, permissions, and acceptance properly.

### Manual Verification
- Log in as User A, invite User B.
- See pending invitation in the list.
- Log out, open the invitation link.
- Register/Login as User B, accept the invitation.
- Verify User B now has access to the workspace.
- Switch between User B's personal workspace and User A's shared workspace.
