# Stage 6: Hackathon Import/Export API

## Implementation Summary
- **JSON Schemas**: Created `HackathonExport`, `HackathonRoundExport`, `HackathonRequirementExport`, and `HackathonImportRequest` using Pydantic in `app/schemas/hackathon_export.py`. This ensures strict validation of payloads.
- **Export Endpoint**: Added `GET /api/v1/hackathon-sync/{hackathon_id}/export`. The backend retrieves the Hackathon entity, its associated Rounds, and Submission Requirements, serializing them into a standard JSON payload.
- **Import Endpoint**: Added `POST /api/v1/hackathon-sync/import`. It expects the same JSON payload alongside a target `workspace_id`. It dynamically provisions a new Hackathon, its Rounds, and Submission Requirements under the specified workspace.

Stage 6 complete. Proceeding to Background Job Architecture.
