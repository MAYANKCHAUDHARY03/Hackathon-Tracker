# Hackathon API Report

## Completion Gate

This report signifies the completion of the authenticated Hackathon backend vertical slice for Phase 2 of Hackathon Tracker.

## Implemented Features

1. **Hackathon Data Model**: Updated the `Hackathon` model in `backend/app/models/hackathon.py` with all requested fields, utilizing `archived_at` for soft deletion according to the existing project architecture (from `SoftDeletable`).
2. **Pydantic Validation Schemas**: Created comprehensive request/response schemas in `backend/app/schemas/hackathon.py`, ensuring:
   - Valid URL formats.
   - Constrained `mode` (`online`, `offline`, `hybrid`) and `status` (`draft`, `upcoming`, `active`, `completed`, `archived`).
   - Chronological validation of dates (`registration_deadline` <= `start_date` <= `end_date`).
   - Positive `max_team_size`.
3. **Workspace RBAC Dependencies**: Added `verify_workspace_access` and `require_workspace_admin` in `backend/app/dependencies.py` to enforce role-based access to workspace resources. 
   - A critical SQLite UUID cast bug was fixed where SQLAlchemy UUID columns expected `UUID` objects instead of `str`.
4. **Hackathon Service Layer**: Developed `HackathonService` in `backend/app/services/hackathon_service.py` with business logic mapping to the controller layer. Provides robust filtering, search, and pagination.
5. **Hackathon Endpoints**: Implemented and documented all standard REST endpoints in `backend/app/routers/hackathons.py`:
   - `POST /api/v1/workspaces/{workspace_id}/hackathons/`
   - `GET /api/v1/workspaces/{workspace_id}/hackathons/`
   - `GET /api/v1/workspaces/{workspace_id}/hackathons/{hackathon_id}`
   - `PUT /api/v1/workspaces/{workspace_id}/hackathons/{hackathon_id}`
   - `POST /api/v1/workspaces/{workspace_id}/hackathons/{hackathon_id}/archive`
   - `POST /api/v1/workspaces/{workspace_id}/hackathons/{hackathon_id}/restore`
   - `DELETE /api/v1/workspaces/{workspace_id}/hackathons/{hackathon_id}`
6. **SQLite Migrations**: Handled SQLite-specific constraints by explicitly naming the foreign keys in the Alembic migration script (`backend/alembic/versions/d9686c9452d9_add_hackathons.py`) using `op.batch_alter_table`.
7. **Integration Tests**: Achieved successful execution of integration tests with completely isolated database workspaces covering creation, retrieval, validation failure modes, workspace boundaries, and lifecycle states (archive/restore/delete).

## Test Verification

All integration tests pass properly, isolating users from different workspaces and restricting create/update/archive permissions to `admin` and `owner` roles as mandated by the implementation plan.

```
tests/test_hackathons.py::test_create_hackathon PASSED
tests/test_hackathons.py::test_unauthenticated_create PASSED
tests/test_hackathons.py::test_invalid_date_order PASSED
tests/test_hackathons.py::test_invalid_url PASSED
tests/test_hackathons.py::test_list_and_retrieve PASSED
tests/test_hackathons.py::test_workspace_isolation PASSED
tests/test_hackathons.py::test_update_hackathon PASSED
tests/test_hackathons.py::test_archive_restore_delete PASSED
```

## Decisions

- **Timestamps:** Timezone-aware UTC datetimes are preserved down through Pydantic to the SQLAlchemy ORM layer. 
- **Roles:** Hackathon creation, updates, and hard deletion are strictly governed by `require_workspace_admin`.
- **Soft Deletes:** `archive` and `restore` endpoints correctly manipulate `status` and `archived_at` in tandem.
