# Phase 4 Kanban Task Execution and Activity History Implementation Plan

## 1. Goal Description
The objective of Phase 4 is to convert each project into an operational execution workspace where authorized team members can manage a Kanban board, tasks, columns, labels, assignments, and track project activity. 

Additionally, because the Phase 3 backend APIs for Teams and Projects were never implemented (a critical regression identified in Stage 0), this plan includes implementing the minimal necessary Team and Project endpoints to unblock the Kanban workflow.

## 2. Open Questions & Critical Dependencies
> [!IMPORTANT]
> **Phase 3 APIs:** Should I fully build out the Phase 3 frontend pages for Teams and Projects, or just the backend APIs so we can programmatically provision them for the Phase 4 Kanban tests?
> *My recommendation:* I will build the backend APIs for Teams and Projects completely, but for the frontend, I will focus the UI effort strictly on the Kanban Board integrated into the Project detail view, skipping the complex "Team management" frontend pages to save time unless specifically requested.

> [!NOTE]
> **Task Ordering Strategy:** For drag-and-drop reordering, using naive `max(position) + 1` is prone to concurrent update conflicts and heavy recalculations on moves. 
> *My recommendation:* I will use **fractional ranking (float `position`)** for tasks and columns. When an item is moved between A and B, its new position is `(A.position + B.position) / 2`. If precision is lost, we trigger a background/inline normalization.

## 3. Proposed Changes

### Database & Models Foundation (Stage 1)
#### [NEW] `backend/app/models/kanban.py`
- `KanbanBoard`: `id`, `workspace_id`, `project_id`, `name`, timestamps.
- `KanbanColumn`: `id`, `board_id`, `name`, `semantic_type` (backlog, todo, in_progress, review, done), `position` (float), `wip_limit`.
- `Task`: `id`, `board_id`, `column_id`, `title`, `description`, `priority`, `position` (float), `due_at`, `started_at`, `completed_at`, `version` (optimistic concurrency integer).
- `TaskLabel`, `TaskLabelAssignment`, `TaskAssignee`.

#### [NEW] `backend/app/models/activity.py`
- `ActivityEvent`: `id`, `workspace_id`, `project_id`, `board_id`, `actor_id`, `entity_type`, `entity_id`, `action`, `safe_metadata` (JSON), `created_at`.

#### [NEW] `backend/alembic/versions/`
- Alembic migration to create Kanban & Activity tables.
- Includes a backfill script in the `upgrade()` block to ensure every existing `Project` gets a default `KanbanBoard` and the 5 default `KanbanColumn`s.

---

### Backend API & Services (Stage 2 & Unblocking Phase 3)
#### [NEW] `backend/app/routers/teams.py` & `backend/app/services/team_service.py`
- Endpoints to create team, list teams, and add members (required to support task assignment).

#### [NEW] `backend/app/routers/projects.py` & `backend/app/services/project_service.py`
- Endpoints to create and list projects (required to anchor the Kanban board).

#### [NEW] `backend/app/routers/kanban.py` & `backend/app/services/kanban_service.py`
- **Board Ops:** `GET /projects/{project_id}/board` (creates default board if missing).
- **Column Ops:** `POST`, `PUT`, `DELETE`, `POST /reorder`.
- **Task Ops:** `POST`, `PUT`, `DELETE` (archive), `POST /move` (handles optimistic concurrency `version`), `POST /assign`, `POST /labels`.

#### [NEW] `backend/app/routers/activity.py` & `backend/app/services/activity_service.py`
- Internal service to write immutable `ActivityEvent`s.
- `GET /projects/{project_id}/activity` with cursor pagination.
- `GET /projects/{project_id}/progress` for summary statistics (completion percentage, open tasks, etc).

---

### Frontend Features (Stage 3 & 4)
#### [NEW] `src/features/kanban/`
- `components/KanbanBoard.tsx`: Main board using `@dnd-kit` for drag-and-drop.
- `components/KanbanColumn.tsx`: Renders tasks and enforces WIP limits visually.
- `components/KanbanTaskCard.tsx`: Compact display of task info.
- `components/TaskModal.tsx`: Create/Edit task dialog (form with Zod validation).
- `components/FilterBar.tsx`: Priority, Assignee, Label, and text search filters.
- `api/kanbanApi.ts`: React Query hooks / API client wrappers.

#### [NEW] `src/features/activity-log/`
- `components/ActivityFeed.tsx`: Renders the immutable activity events dynamically.
- `components/ProjectProgress.tsx`: Renders the completion percentage and task stats.

#### [MODIFY] `src/pages/Dashboard.tsx`
- Add "My tasks due soon" and "Recent project activity" summaries to the dashboard.

#### [NEW] `src/pages/ProjectDetail.tsx` (Replaces Placeholder)
- Contains the Kanban Board tab and the Activity tab.

## 4. Verification Plan

### Automated Tests
- **Backend:** Add `tests/test_kanban.py` to verify board backfill, column defaults, task fractional reordering, WIP limits, optimistic concurrency (409 Conflict), and cross-workspace isolation.
- **Frontend:** Build passes `npm run build`, lint passes.

### Browser Verification (Stage 5)
1. Register 2 users in the same workspace.
2. Programmatically or manually create a Hackathon, Team, and Project.
3. Open the Project Kanban board.
4. Verify default columns exist. Create tasks, set priorities/labels/due dates.
5. Drag and drop tasks between columns (ensure `completed_at` triggers on moving to Done).
6. Verify Activity log displays natural language events (e.g., "User moved task to Done").
7. Ensure removed users lose board access instantly.
