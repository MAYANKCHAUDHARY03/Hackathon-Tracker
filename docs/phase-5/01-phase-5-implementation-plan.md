# Phase 5 Implementation Plan: Rounds, Deadlines, and Submission Management

## 1. Domain Foundation & Database Modeling
We will introduce models and schemas to track hackathon rounds, deadlines, and submissions.

**Files to modify/create:**
- `backend/app/models/hackathon.py`: Add `timezone` (String, default UTC for new, nullable for existing backfill).
- `backend/app/models/round.py` [NEW]:
  - `HackathonRound`
  - `Deadline`
  - `RoundProgress`
- `backend/app/models/submission.py` [NEW]:
  - `SubmissionRequirement`
  - `RoundSubmission`
  - `SubmissionItem`
  - `SubmissionSnapshot` (or JSONB snapshot column in RoundSubmission for immutable records).
- `backend/app/schemas/round.py` [NEW]
- `backend/app/schemas/submission.py` [NEW]
- `backend/alembic/versions/...` [NEW]: Migrations for Timezone and new tables.

## 2. Service Layer & Business Logic
Implement services to manage CRUD operations, validation logic, readiness calculations, and authorization.

**Files to modify/create:**
- `backend/app/services/round_service.py` [NEW]: Handle rounds, ordering (transactional), deadlines, and team progress.
- `backend/app/services/submission_service.py` [NEW]: Handle requirements, submissions, item validation (URL schemes, lengths), readiness calculation, and state machine transitions (Draft -> Ready -> Submitted -> Locked). Includes activity event generation.
- `backend/app/services/activity_service.py`: Add event types for submissions and rounds.

## 3. API Routers
Expose REST endpoints reflecting the required operations.

**Files to modify/create:**
- `backend/app/routers/rounds.py` [NEW]
- `backend/app/routers/submissions.py` [NEW]
- `backend/app/main.py`: Include new routers.

## 4. Frontend Integration & Infrastructure
Create API client integrations to talk to the new backend endpoints.

**Files to modify/create:**
- `src/api/roundApi.ts` [NEW]
- `src/api/submissionApi.ts` [NEW]

## 5. UI Implementation
Build the frontend interfaces for rounds, deadlines, calendar, timeline, and submission workspace.

**Files to modify/create:**
- `src/pages/HackathonDetails.tsx` (or new component): Build the Rounds timeline, Deadline lists, and Timeline view.
- `src/pages/Calendar.tsx`: Connect existing Calendar shell to fetch and display actual Deadlines/Rounds.
- `src/pages/ProjectDetail.tsx` (or new Submission component): Rebuild as the team Submission Workspace.
  - Implement Requirement listing, Project prefill, validation states, readiness display, and finalization controls.
- `src/components/dashboard/UpcomingDeadlines.tsx` [NEW]: Component for dashboard.
- `src/components/dashboard/ActionItems.tsx` [NEW]: Component for action items (missing items, overdue submissions).
- `src/pages/Dashboard.tsx`: Integrate summary components.

## 6. Testing & Quality Assurance
Write comprehensive backend tests and verify frontend behaviour.

**Files to modify/create:**
- `backend/tests/test_rounds.py` [NEW]
- `backend/tests/test_submissions.py` [NEW]
- Run all manual end-to-end browser workflows detailed in Stage 7 of the specification.
