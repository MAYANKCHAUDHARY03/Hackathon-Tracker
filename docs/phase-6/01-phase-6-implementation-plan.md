# Phase 6 Implementation Plan — Notifications, Evaluation & Hackathon Outcomes

## Goal

Add four connected capabilities to the hackathon tracker:
1. In-app notification and reminder centre
2. Mentor and judge information management
3. Structured evaluation criteria and scorecards
4. Results, rewards, and achievement history

## Pre-Implementation Fixes

Before Phase 6 work begins, repair these issues discovered during audit:

1. **Fix `activity_service.py`** — change `user_id=user_id` to `actor_id=user_id` to match the `ActivityEvent` model
2. **Fix `submission_service.py`** — replace `datetime.utcnow()` with `datetime.now(timezone.utc)`
3. **Add database files to `.gitignore`** — `*.db`, `*.sqlite`
4. **Commit all Phase 3–5 work** as a baseline before Phase 6 changes

---

## Proposed Changes

### Stage 1 — Notification Domain Foundation

#### Backend Models

##### [NEW] `backend/app/models/notification.py`
- `Notification` model with all required fields (id, workspace_id, recipient_user_id, notification_type, category, severity, title, body, action_url, entity_type, entity_id, event_key, metadata, occurred_at, read_at, dismissed_at, expires_at, created_at, updated_at)
- `NotificationPreference` model (id, workspace_id nullable, user_id, category, in_app_enabled, reminder_offsets, quiet_hours_enabled, quiet_hours_start, quiet_hours_end, timezone, created_at, updated_at)
- Enum values for categories (deadline, task, round, submission, team, project, evaluation, result, reward, system)
- Enum values for severity (info, success, warning, urgent)
- Composite indexes for efficient querying
- Unique constraint on event_key for idempotency

##### [MODIFY] `backend/app/models/__init__.py`
- Import and export new Notification and NotificationPreference models

##### [NEW] `backend/app/schemas/notification.py`
- Pydantic schemas: NotificationResponse, NotificationListResponse, NotificationPreferenceCreate/Update/Response, NotificationSummaryResponse, MarkReadRequest

##### [NEW] `backend/app/services/notification_service.py`
- `create_notification()` — with event_key dedup, workspace access verification, action_url validation
- `get_notifications()` — filtered by recipient, category, severity, read status, workspace, date range, with pagination
- `get_unread_count()` — efficient COUNT query
- `mark_read()`, `mark_all_read()`, `dismiss()`, `restore_dismissed()`
- `get_preferences()`, `update_preferences()`
- `get_notification_summary()` — aggregated counts by category
- `cleanup_expired()` — safe cleanup respecting urgent/unread rules

##### [NEW] `backend/app/services/recipient_service.py`
- `resolve_recipients()` — determines who should receive a notification based on event type
- Handles: task assignees, team members, team leads, project members
- Filters out removed users (left_at is set)

##### [NEW] `backend/app/routers/notifications.py`
- GET `/workspaces/{workspace_id}/notifications` — list with filters
- GET `/workspaces/{workspace_id}/notifications/unread-count`
- GET `/workspaces/{workspace_id}/notifications/summary`
- GET `/workspaces/{workspace_id}/notifications/{id}`
- POST `/workspaces/{workspace_id}/notifications/{id}/read`
- POST `/workspaces/{workspace_id}/notifications/read-all`
- POST `/workspaces/{workspace_id}/notifications/{id}/dismiss`
- POST `/workspaces/{workspace_id}/notifications/{id}/restore`
- GET `/workspaces/{workspace_id}/notification-preferences`
- PUT `/workspaces/{workspace_id}/notification-preferences`

##### [NEW] `backend/alembic/versions/xxx_add_notification_models.py`
- Migration for notifications and notification_preferences tables

---

### Stage 2 — Reminder and Event Generation Engine

##### [NEW] `backend/app/services/notification_events.py`
- Event handler functions that create notifications for:
  - Task assigned, task due soon, task overdue
  - Deadline due soon, deadline overdue
  - Round starting soon
  - Submission incomplete near deadline, submission ready, submitted, locked
  - Round progress changed
  - Team member added/removed
  - Project archived
  - Evaluation recorded, result recorded, reward/achievement recorded
- Each function uses `notification_service.create_notification()` with stable event_keys

##### [NEW] `backend/app/jobs/__init__.py`
##### [NEW] `backend/app/jobs/generate_reminders.py`
- CLI-executable reminder generation job
- Scans upcoming deadlines, task due dates, round start dates
- Generates reminders at configurable offsets (24h, 6h, 1h before)
- Idempotent via event_key: `f"reminder:{entity_type}:{entity_id}:{offset}:{due_date}"`
- Respects quiet hours (creates notification but marks for deferred visibility)
- Entry point: `python -m app.jobs.generate_reminders`

##### [NEW] `backend/app/jobs/cleanup_notifications.py`
- Removes expired notifications (where expires_at < now AND read_at is set)
- Removes old dismissed notifications (> 90 days)
- Never deletes unread urgent notifications
- Entry point: `python -m app.jobs.cleanup_notifications`

##### Integration with existing services
- [MODIFY] `backend/app/services/kanban_service.py` — call notification_events after task assignment/movement
- [MODIFY] `backend/app/services/submission_service.py` — call notification_events after submission state changes
- [MODIFY] `backend/app/services/round_service.py` — call notification_events after round/deadline changes

---

### Stage 3 — Mentors and Judges Domain

##### [NEW] `backend/app/models/people.py`
- `Person` model (shared contact entity for mentors/judges):
  - id, workspace_id, full_name, organisation, designation, expertise_areas (JSON array), bio, public_profile_url, email, phone, visibility (workspace/team/private), created_by, updated_by, created_at, updated_at, archived_at
- `MentorAssignment` model:
  - id, workspace_id, hackathon_id, round_id (nullable), team_id (nullable), mentor_id (FK to Person), topic, session_at, notes, status (planned/completed/cancelled/archived), created_by, updated_by, created_at, updated_at, archived_at
- `JudgeAssignment` model:
  - id, workspace_id, hackathon_id, round_id (nullable), judge_id (FK to Person), role, panel_name, assignment_notes, created_by, updated_by, created_at, updated_at, archived_at
  - Unique constraint on (hackathon_id, round_id, judge_id)

##### [NEW] `backend/app/schemas/people.py`
- PersonCreate, PersonUpdate, PersonResponse (with field-level privacy filtering), PersonListResponse
- MentorAssignmentCreate, MentorAssignmentUpdate, MentorAssignmentResponse
- JudgeAssignmentCreate, JudgeAssignmentUpdate, JudgeAssignmentResponse

##### [NEW] `backend/app/services/people_service.py`
- Person CRUD with privacy-safe responses
- Mentor assignment CRUD with workspace/hackathon/team validation
- Judge assignment CRUD with duplicate prevention
- Archive/restore functionality
- Expertise search

##### [NEW] `backend/app/routers/mentors.py`
- Workspace-scoped mentor CRUD and assignment endpoints

##### [NEW] `backend/app/routers/judges.py`
- Workspace-scoped judge CRUD and assignment endpoints

##### [NEW] `backend/alembic/versions/xxx_add_people_models.py`

---

### Stage 4 — Evaluation Criteria and Scorecards

##### [NEW] `backend/app/models/evaluation.py`
- `EvaluationTemplate`:
  - id, workspace_id, hackathon_id, round_id (nullable), name, description, scoring_method (weighted/points/pass_fail), maximum_total_score, status (draft/active/locked/archived), created_by, updated_by, timestamps, archived_at
- `EvaluationCriterion`:
  - id, workspace_id, template_id, name, description, weight (Numeric), maximum_score (Numeric), position, is_required, timestamps, archived_at
- `Evaluation`:
  - id, workspace_id, hackathon_id, round_id, team_id, project_id, template_id, evaluator_person_id (nullable FK to Person), evaluator_name_snapshot, status (draft/completed/locked/archived), total_score (Numeric), maximum_score (Numeric), percentage (Numeric), overall_feedback, source, evaluated_at, created_by, updated_by, timestamps, locked_at
  - Template/criteria snapshot stored as JSON
- `EvaluationScore`:
  - id, evaluation_id, criterion_id, criterion_name_snapshot, weight_snapshot (Numeric), maximum_score_snapshot (Numeric), numeric_score (Numeric, nullable), pass_value (Boolean, nullable), feedback, timestamps

##### [NEW] `backend/app/schemas/evaluation.py`
- All create/update/response schemas for templates, criteria, evaluations, scores
- Calculation preview response

##### [NEW] `backend/app/services/evaluation_service.py`
- Template CRUD with status transitions (draft → active → locked)
- Criterion CRUD with transactional reordering
- Weight validation (total = 100 for weighted, with tolerance)
- Evaluation creation with snapshot capture
- Score entry with type validation (numeric for weighted/points, boolean for pass_fail)
- Server-side calculation using Decimal for precision
- Weighted formula: `sum((score / max) × weight)`
- Points formula: `sum(score) / sum(max) × 100`
- Lock evaluation (immutable after)
- Archive/restore

##### [NEW] `backend/app/routers/evaluations.py`
- Full CRUD endpoints under workspace scope

##### [NEW] `backend/alembic/versions/xxx_add_evaluation_models.py`

---

### Stage 5 — Results, Rewards and Achievements

##### [NEW] `backend/app/models/outcome.py`
- `HackathonResult`:
  - id, workspace_id, hackathon_id, team_id, project_id, round_id (nullable), result_type, position (nullable), title, description, status, announced_at, source_url, is_verified (default False), verification_note, created_by, updated_by, timestamps, archived_at
- `Reward`:
  - id, workspace_id, hackathon_id, team_id (nullable), result_id (nullable), title, reward_type, monetary_value (Numeric, nullable), currency (nullable), sponsor, description, status, received_at, created_by, updated_by, timestamps, archived_at
- `Achievement`:
  - id, workspace_id, user_id (nullable), team_id (nullable), hackathon_id, project_id (nullable), result_id (nullable), achievement_type, title, description, achieved_at, visibility, source, created_by, updated_by, timestamps, archived_at

##### [NEW] `backend/app/schemas/outcome.py`
##### [NEW] `backend/app/services/outcome_service.py`
- Result CRUD, reward CRUD, achievement CRUD
- Achievement generation from results (propagate to active team members)
- Duplicate achievement prevention
- Team/user outcome summaries

##### [NEW] `backend/app/routers/results.py`
##### [NEW] `backend/app/routers/rewards.py`
##### [NEW] `backend/app/routers/achievements.py`
##### [NEW] `backend/alembic/versions/xxx_add_outcome_models.py`

---

### Stage 6 — Frontend Notification Centre

##### [NEW] `src/api/notificationApi.ts`
- API client functions for all notification endpoints

##### [NEW] `src/hooks/useNotifications.ts`
- Custom hook for notification listing, unread count, mark read, dismiss

##### [NEW] `src/store/notificationStore.ts`
- Zustand store for unread count (polled periodically)

##### [NEW] `src/components/notifications/NotificationBell.tsx`
- Unread count badge + dropdown with recent notifications

##### [NEW] `src/components/notifications/NotificationDropdown.tsx`
- Recent notifications with mark read, view all link

##### [NEW] `src/pages/Notifications.tsx`
- Full notification centre with tabs (unread/all), category filters, severity filters, pagination

##### [NEW] `src/pages/NotificationPreferences.tsx`
- Category toggles, reminder offsets, quiet hours, timezone

##### [MODIFY] `src/components/layout/Topbar.tsx`
- Replace static bell with NotificationBell component

##### [MODIFY] `src/router/index.tsx`
- Add `/notifications` and `/notifications/preferences` routes

---

### Stage 7 — Mentors, Judges and Evaluation Frontend

##### [NEW] `src/api/peopleApi.ts`
##### [NEW] `src/api/evaluationApi.ts`
##### [NEW] `src/hooks/useMentors.ts`
##### [NEW] `src/hooks/useJudges.ts`
##### [NEW] `src/hooks/useEvaluations.ts`

##### [NEW] `src/pages/Mentors.tsx`
- Mentor list, create, edit, detail, expertise search, assignments

##### [NEW] `src/pages/Judges.tsx`
- Judge list, create, edit, detail, round assignments

##### [NEW] `src/pages/EvaluationTemplates.tsx`
- Template list, create, scoring method selection, criteria management

##### [NEW] `src/pages/Scorecard.tsx`
- Score entry form, criterion feedback, calculated preview, save draft, complete, lock

##### [NEW] `src/components/evaluation/CriterionList.tsx`
- Drag-to-reorder criteria, weight/score inputs, validation

##### [NEW] `src/components/evaluation/ScoreInput.tsx`
- Score input appropriate to scoring method (numeric slider/input for weighted/points, toggle for pass_fail)

##### [NEW] `src/components/evaluation/EvaluationSummary.tsx`
- Score breakdown, percentage, feedback display

##### [MODIFY] `src/components/layout/Sidebar.tsx`
- Add Mentors and Judges nav items

##### [MODIFY] `src/router/index.tsx`
- Add mentor, judge, evaluation routes

---

### Stage 8 — Results, Rewards and Achievement Frontend

##### [NEW] `src/api/outcomeApi.ts`
##### [NEW] `src/hooks/useOutcomes.ts`

##### [NEW] `src/pages/Outcomes.tsx`
- Results, rewards, achievements under hackathon context

##### [NEW] `src/pages/AchievementHistory.tsx`
- User's authenticated achievement history with filters

##### [NEW] `src/components/outcome/ResultCard.tsx`
##### [NEW] `src/components/outcome/RewardCard.tsx`
##### [NEW] `src/components/outcome/AchievementCard.tsx`

##### [MODIFY] `src/pages/Dashboard.tsx`
- Add Phase 6 widgets: unread notifications, evaluations awaiting, recent results, achievements

##### [MODIFY] `src/pages/HackathonDetails.tsx`
- Add Outcomes tab/section

##### [MODIFY] `src/router/index.tsx`
- Add outcome and achievement routes

---

### Stage 9–10 — Testing and Verification

##### [NEW] `backend/tests/test_notifications.py`
- Event generation, recipient resolution, duplicate prevention, mark read, dismiss, preferences, quiet hours, workspace isolation

##### [NEW] `backend/tests/test_people.py`
- Mentor/judge CRUD, privacy filtering, assignments, cross-workspace isolation

##### [NEW] `backend/tests/test_evaluations.py`
- Template CRUD, criterion ordering, weighted calculation, points calculation, pass/fail, decimal precision, locked mutation rejection, snapshot integrity

##### [NEW] `backend/tests/test_outcomes.py`
- Result CRUD, reward CRUD, achievement generation, duplicate prevention, removed-member policy

##### [NEW] `backend/tests/test_reminder_job.py`
- Idempotent reminder generation, duplicate prevention, changed due dates

---

## Verification Plan

### Automated Tests
- `cd backend && python -m pytest tests/ -v`
- `cd . && npx tsc --noEmit` (frontend typecheck)
- `npm run lint`
- `npm run build` (production build)

### Manual Verification
- Browser-based end-to-end flow covering all 57 steps in Stage 9
- Desktop, tablet, and mobile layout verification
- Two-account testing for notification delivery and privacy

---

## Open Questions

> [!IMPORTANT]
> **Workspace scoping pattern**: The existing codebase uses two patterns — path parameter (`/workspaces/{workspace_id}/...`) for hackathons and header (`x-workspace-id`) for rounds/submissions. Phase 6 will use the path parameter pattern consistently for new endpoints, matching the hackathon router convention. This is the more explicit and RESTful approach.

> [!NOTE]
> **No TanStack Query**: The frontend uses manual `useState`/`useEffect` patterns. Phase 6 will follow this existing convention. Adding TanStack Query would be a valuable improvement but is a cross-cutting refactor better suited for Phase 7.

> [!NOTE]
> **Activity event model**: The existing `ActivityEvent` model is tightly coupled to projects (`project_id` is required). Phase 6 will extend it with optional `hackathon_id` to support evaluation, result, and achievement events that may not be project-specific.
