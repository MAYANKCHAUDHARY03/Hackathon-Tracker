# Stage 5: External Calendars

## Implementation Summary
- **CalendarIntegration Model**: Added a new table to store OAuth credentials (`access_token`, `refresh_token`, etc.) linked to a specific workspace and provider (`google` or `outlook`).
- **Calendar Service**: Added `app/services/calendar_service.py` to push event payloads to Google Calendar and Microsoft Graph (Outlook).
- **Timeouts & Reliability**: Integrated `httpx.AsyncClient` with a strict `timeout=10.0` for all external calls.
- **Error Handling**: Implemented catch and formatting for `401 Unauthorized` responses and external API errors.
- **Milestone Mapping**: Created `sync_hackathon_to_calendars` helper function that can take hackathon event data and push it across all active calendar integrations for a workspace.

Stage 5 complete. Proceeding to Hackathon Import/Export API.
