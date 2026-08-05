# Phase 3 Implementation Plan

## Overview
Phase 3 introduces Team Collaboration and Project Workspaces. This plan maps the current Phase 2 codebase (Auth, Workspaces, Hackathons CRUD) to the new requirements of Phase 3, outlining the necessary architectural extensions.

## Codebase Mapping & Implementation Steps

### 1. Workspace Invitations
- **Backend**: 
  - `app/models/workspace.py`: Add `WorkspaceInvitation` model to handle pending, accepted, expired, and revoked invites. Token hash stored securely.
  - `app/routers/workspaces.py`: Endpoints for inviting users, revoking, listing, and accepting invitations.
  - `app/schemas/workspace.py`: Add invitation schemas.
- **Frontend**: 
  - `src/features/workspaces/`: Add invitation dialogs, lists, and acceptance routes.

### 2. Workspace Switching
- **Backend**: API relies on `WorkspaceMembership` validation (already largely present). Must ensure users can query all their active workspaces.
- **Frontend**: 
  - `src/store/workspaceStore.ts`: Update to manage an active selected workspace. Persist selection via `localStorage` or session state.
  - `src/components/layout/Topbar.tsx` & `Sidebar.tsx`: Add a dropdown to switch workspaces smoothly without logout.

### 3. Teams & Team Memberships
- **Backend**:
  - `app/models/team.py` (New): `Team` model (linked to workspace & hackathon) and `TeamMember` model (linked to team & user, storing roles and specialties).
  - `app/routers/teams.py` (New): Endpoints for CRUD on teams and membership management.
  - `app/schemas/team.py` (New): Pydantic validation schemas.
- **Frontend**:
  - `src/features/teams/` (New): Views for listing teams, creating teams, and managing team rosters (adding members, changing roles).

### 4. Projects & Technologies
- **Backend**:
  - `app/models/project.py` (New): `Project` model (linked to team), `Technology` dictionary model, and `ProjectTechnology` join table.
  - `app/routers/projects.py` (New): Endpoints for project CRUD and stack management.
  - `app/schemas/project.py` (New): Validation schemas.
- **Frontend**:
  - `src/features/projects/` (New): UI for creating projects, displaying statuses, entering links (repo, demo), and assigning technologies.

### 5. Frontend Integration
- **Hackathon Page**: Integrate "Teams" and "Projects" tabs or sections directly within the Hackathon detail view to establish the Hackathon -> Team -> Project flow.
- **Dashboard**: Provide new stats (total teams, total projects, recent updates).
- **Navigation**: Update Sidebar and Breadcrumbs to reflect the new hierarchy.

### 6. Authorization Extensions
- **Backend Services**: Extend `app/services/auth_service.py` (or similar) to include permission checks for `team_lead`, `team_co_lead`, and `team_member`. Ensure all queries validate `workspace_id`.
- **Frontend Guards**: Introduce UI-level permission checks to hide destructive actions (e.g., Delete Project) from unauthorized members.

### 7. Migrations
- Generate Alembic migrations for new models: `WorkspaceInvitation`, `Team`, `TeamMember`, `Project`, `Technology`, `ProjectTechnology`.
- Carefully apply cross-table unique constraints (e.g., one project per team, unique active membership per user per hackathon).

### 8. Tests
- Add Pytest coverage for all new routers and business rules (e.g., rejecting an invite twice, preventing a user from joining two teams in one hackathon).
- Enhance frontend component tests (if applicable) and manually verify layouts.

### 9. Browser Verification
- Smoke test the complete E2E flow: Invite -> Accept -> Switch Workspace -> Hackathon -> Team -> Member Add -> Project -> Tech Stack. 

## Phase 3 Risks & Affected Files
- **Risks**:
  - **State Management**: Managing `activeWorkspace` in the frontend might cause stale data if caches aren't invalidated correctly upon switching.
  - **Auth Complexity**: Moving from Workspace roles to Team roles adds a secondary layer of authorization that could cause 403 bugs if misaligned.
  - **Database Constraints**: SQLite lacks some advanced constraint features; we must handle rules meticulously in the service layer where DB constraints fall short (or utilize SQLAlchemy hybrid properties).
- **Affected Core Files**:
  - `app/models/__init__.py`
  - `app/main.py` (registering new routers)
  - `src/router/index.tsx`
  - `src/store/workspaceStore.ts`
  - `src/pages/Dashboard.tsx`
  - `src/pages/HackathonDetail.tsx` (or equivalent)
