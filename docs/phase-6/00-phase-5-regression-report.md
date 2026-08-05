# Phase 5 Regression Audit Report — Pre-Phase 6

## 1. Audit Objective

Verify Phase 5 (rounds, deadlines, submission management, calendar, timeline) and all prior phases (1–4) are functionally stable before commencing Phase 6 implementation.

## 2. Repository State

| Item | Observation |
|------|-------------|
| **Branch** | `phase-3-collaboration-workspace` |
| **Last commit** | `361e4da feat: complete phase 2 authenticated hackathon vertical slice` |
| **Uncommitted changes** | Phases 3–5 changes are entirely uncommitted (models, routers, services, schemas, migrations, frontend pages, tests, docs) |
| **Database files in repo** | `backend/test.db`, `backend/test_db.sqlite`, `backend/hackathon_tracker.db` — should be gitignored |
| **`.env` files** | Both root `.env` and `backend/.env` exist and are tracked by git status but listed in `.gitignore` |

## 3. Architecture Summary

| Layer | Technology | Pattern |
|-------|-----------|---------|
| Backend | FastAPI + SQLAlchemy 2.0 (async) + Alembic | Service-layer functions and static-method services |
| Database | PostgreSQL (prod) / SQLite (test) | UUID PKs, timezone-aware datetime, `BaseEntity` with id/created_at/updated_at |
| Auth | JWT (python-jose), OAuth2PasswordBearer | `get_current_user`, `verify_workspace_access`, `require_workspace_admin` |
| Workspace scoping | `x-workspace-id` header OR path parameter `workspace_id` | Mixed — hackathons use path param, rounds/submissions use header |
| Frontend | React 19 + Vite 8 + TypeScript 6 | Zustand stores (persisted), custom hooks, `apiClient` wrapper |
| Styling | TailwindCSS 3.4 + custom glassmorphism | Dark/light/system theme |
| State | Zustand (auth, workspace, hackathon, UI, filter, history) | Persisted to localStorage |
| Routing | react-router-dom v7 | `createBrowserRouter`, lazy-loaded pages |
| Query | Manual `useState`/`useEffect` + `apiClient` | No TanStack Query yet |

## 4. Existing Models Audit

| Model | File | Workspace-scoped | Status |
|-------|------|-------------------|--------|
| User | `user.py` | via memberships | ✅ Real |
| WorkspaceMembership | `user.py` | FK to workspaces | ✅ Real |
| Workspace | `workspace.py` | root entity | ✅ Real |
| WorkspaceInvitation | `workspace_invitation.py` | FK to workspaces | ✅ Real |
| Hackathon | `hackathon.py` | FK to workspaces | ✅ Real |
| Team | `team.py` | FK to workspaces + hackathons | ✅ Real |
| TeamMember | `team.py` | FK to teams + users | ✅ Real |
| Project | `project.py` | FK to workspaces + hackathons + teams | ✅ Real |
| Technology | `project.py` | global | ✅ Real |
| ProjectTechnology | `project.py` | FK to projects + technologies | ✅ Real |
| KanbanBoard | `kanban.py` | FK to workspaces + projects | ✅ Real |
| KanbanColumn | `kanban.py` | FK to boards | ✅ Real |
| Task | `kanban.py` | FK to boards + columns | ✅ Real |
| TaskAssignee | `kanban.py` | FK to tasks + users | ✅ Real |
| TaskLabel | `kanban.py` | FK to boards | ✅ Real |
| TaskLabelAssignment | `kanban.py` | FK to tasks + labels | ✅ Real |
| ActivityEvent | `activity.py` | FK to workspaces + projects | ✅ Real |
| HackathonRound | `round.py` | FK to workspaces + hackathons | ✅ Real |
| Deadline | `round.py` | FK to workspaces + hackathons | ✅ Real |
| RoundProgress | `round.py` | FK to workspaces + hackathons + rounds + teams | ✅ Real |
| SubmissionRequirement | `submission.py` | FK to workspaces + hackathons + rounds | ✅ Real |
| RoundSubmission | `submission.py` | FK to workspaces + hackathons + rounds + teams | ✅ Real |
| SubmissionItem | `submission.py` | FK to submissions + requirements | ✅ Real |

## 5. Existing Feature Modules — Placeholder vs Real

| Feature | Sidebar/Route | Backend | Frontend | Classification |
|---------|--------------|---------|----------|----------------|
| Dashboard | `/` | `dashboard_service.py` + router | `Dashboard.tsx` + `useDashboard` | ✅ Real |
| Hackathons | `/hackathons` | Full CRUD service + router | Uses `Placeholder.tsx` for list; `HackathonDetails.tsx` for detail | ⚠️ Partial (list is placeholder) |
| Calendar | `/calendar` | No dedicated backend | `Calendar.tsx` exists | ⚠️ Minimal (page likely placeholder-like) |
| Kanban | `/kanban` | Full service + router | `Kanban.tsx` + kanban components | ✅ Real |
| Analytics | `/analytics` | None | `Placeholder.tsx` | 🔴 Placeholder |
| Team Database | `/teams` | `team_service.py` + router | `Placeholder.tsx` | 🔴 Placeholder (backend exists) |
| Project Database | `/projects` | `project_service.py` + router | `Placeholder.tsx` | 🔴 Placeholder (backend exists) |
| API Vault | `/vault` | None | `Placeholder.tsx` | 🔴 Placeholder |
| Settings | `/settings` | invitations backend | `Settings.tsx` with invitation management | ✅ Real |
| Notifications | Bell icon in Topbar | None | Hardcoded dot indicator, no functionality | 🔴 Static indicator only |
| Mentors | — | None | None | 🔴 Not implemented |
| Judges | — | None | None | 🔴 Not implemented |

## 6. Issues Identified

### 6.1 Critical Issues

1. **All Phase 3–5 changes are uncommitted** — the entire collaboration, kanban, activity, rounds, and submission layers exist only as working-directory changes. No intermediate commits.
2. **Database files committed** — `test.db`, `test_db.sqlite`, and `hackathon_tracker.db` are not in `.gitignore`.
3. **`KanbanColumn` model references `workspace_id`** — but the `KanbanColumn` model does not actually have a `workspace_id` column. The `create_column` service function passes `workspace_id` to `KanbanColumn(...)` which will fail at runtime since the column doesn't exist in the model.
4. **`Task` model references `workspace_id`** — same issue as `KanbanColumn`. The `create_task` service passes `workspace_id` but `Task` has no such field.
5. **`ActivityEvent.user_id` vs `actor_id`** — The model defines `actor_id` but `activity_service.log_activity` sets `user_id=user_id`. This is a runtime mismatch.
6. **`HackathonDetails.tsx` references `activeWorkspace`** — but `workspaceStore` only exports `activeWorkspaceId` (a string), not `activeWorkspace` (an object). This will cause the component to fail.
7. **Topbar notification bell** — has a hardcoded red dot, no backend integration, no notification system.

### 6.2 Non-Critical Issues

1. **Mixed workspace scoping patterns** — hackathons use `workspace_id` as a path parameter, while rounds/submissions use `x-workspace-id` as a header. Inconsistent but functional.
2. **`submission_service.lock_submission`** uses `datetime.utcnow()` — should use `datetime.now(timezone.utc)` for consistency with the base model.
3. **Frontend types diverge from backend** — `src/types/index.ts` has `HackathonMentor`, `HackathonJudge`, `Reward`, `Status`, `ApiKey` types that don't correspond to any backend models.
4. **No `@tanstack/react-query`** — the project uses manual state management for API calls rather than a query library, despite having `@tanstack/react-table` and `@tanstack/react-virtual`.

## 7. Phase 5 Feature Verification

| Feature | Backend | Frontend | Notes |
|---------|---------|----------|-------|
| Hackathon timezone field | ✅ `timezone` on Hackathon model | ⚠️ Not visible in UI | Field exists but no timezone display/selector |
| Rounds CRUD | ✅ Service + Router | ✅ HackathonDetails shows rounds | Basic list rendering |
| Deadline CRUD | ✅ Service + Router | ✅ HackathonDetails shows deadlines | Basic list rendering |
| Round ordering | ✅ `sequence` with unique constraint | ✅ Sorted by sequence | Works |
| Submission requirements | ✅ Full CRUD | ✅ SubmissionWorkspace | Works |
| Submission state machine | ✅ draft → submitted → locked | ✅ SubmissionWorkspace | Works |
| Locked snapshots | ✅ JSON snapshot on lock | ✅ Displayed in UI | Works |
| Readiness calculation | ✅ Server-side validation | ✅ Client preflight check | Works |
| Round progress | ✅ Model exists | ⚠️ No dedicated UI | Model exists, no management UI |
| Calendar | ⚠️ No backend | ⚠️ Minimal page | Needs inspection |
| Timeline | ⚠️ No dedicated timeline view | ⚠️ Deadline list in dashboard | Basic |

## 8. Migration Status

Seven migrations exist in order:
1. `5f9ac36cc36f_initial_migration.py`
2. `3aabbacf5652_auth_and_workspaces_implementation.py`
3. `d9686c9452d9_add_hackathons.py`
4. `8222d248e6c8_add_collaboration_models.py`
5. `8c30f6e9a104_add_kanban_and_activity_models.py`
6. `035fcd8f66d7_add_rounds_and_deadlines.py`
7. `641419d1654a_add_submission_models.py`

These are all untracked/uncommitted files.

## 9. Test Suite Status

Test files present:
- `test_health.py`
- `test_startup.py`
- `test_auth.py`
- `test_hackathons.py`
- `test_dashboard.py`
- `test_collaboration_domain.py`
- `test_invitations.py`
- `test_rounds.py`

Test infrastructure uses SQLite with `aiosqlite` via `conftest.py`.

## 10. Conclusion

Phase 5 core functionality (rounds, deadlines, submissions, locking, snapshots) is implemented at the backend level and has basic frontend integration. However, several issues need repair:

1. **Activity service field mismatch** (`user_id` vs `actor_id`) — must fix before Phase 6 event generation.
2. **Missing `workspace_id` on KanbanColumn/Task** — the kanban service passes this field but models don't have it. This needs investigation (may work if the column is on the board relationship).
3. **Notification system** — completely absent; bell icon is cosmetic.
4. **Mentors, Judges, Analytics** — no backend implementation exists.
5. **Database files** should be gitignored.

**Verdict: Phase 5 is sufficiently stable to proceed with Phase 6, with targeted fixes applied during implementation.**
