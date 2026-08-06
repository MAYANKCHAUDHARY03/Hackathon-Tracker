# Blank UI Investigation

## Observed Symptoms
* Frontend and backend were reported as running, but the UI displayed a blank screen or a generic "Failed to register" without functionality.
* Attempting to perform API actions resulted in immediate silent failures or generic catch-all errors on the frontend.

## Actual Root Cause
1. **CORS Configuration Mismatch**: The frontend development server frequently runs on port `5174` (when `5173` is busy), but `backend/.env` and `backend/app/config.py` did not explicitly whitelist `http://localhost:5174` in `BACKEND_CORS_ORIGINS`. Additionally, the `.env` `VITE_API_BASE_URL` pointed directly to `http://localhost:8000/api/v1` instead of using the Vite proxy, triggering CORS preflight requests that were being rejected. This led to `fetch()` throwing a generic `TypeError` with no response body, bubbling up to an unhandled exception or an empty error state.
2. **UUID String Mapping Bug**: In the SQLAlchemy models (`app/models/user.py`), `WorkspaceMembership` mapped the UUID foreign keys (`user_id`, `workspace_id`) to `Mapped[str]`. This type mismatch with Postgres `UUID` columns causes an internal server error (500) during database inserts (e.g. user registration or workspace invitation acceptance), triggering a backend crash cascade that left the UI in a broken state if the error detail wasn't properly handled by the frontend.
3. **Frontend Error Handling Limitation**: `Register.tsx` expected `err.data.detail` to be a string. When Pydantic validation arrays or network TypeErrors were thrown, the React state was updated improperly or not at all, leaving users with cryptic fallback errors and breaking the component's state loop.

## Affected Files
* `backend/.env`
* `backend/app/config.py`
* `backend/app/models/user.py`
* `backend/app/routers/auth.py`
* `src/pages/Register.tsx`
* `.env` (frontend)

## Fix Applied
1. **Environment & config updates**: Added dynamic origins (`http://localhost:5174`, `127.0.0.1:5174`) to both frontend and backend configurations for robust CORS handshakes.
2. **UUID schema correction**: Re-mapped `user_id` and `workspace_id` in `WorkspaceMembership` to explicitly use `Mapped[uuid.UUID]`, and removed string casting (`str()`) in `auth.py`.
3. **Robust error boundaries**: Refactored `catch` blocks in frontend forms (like `Register.tsx`) to properly unwrap Pydantic validation arrays (`err.data?.detail[0]?.msg`) and handle pure string errors securely.

## Browser Evidence
* The API endpoints (`/auth/register`, `/users/me`) are now accessible via cross-origin requests.
* The frontend receives and parses valid JSON tracebacks or success payloads rather than blocking on pre-flight checks.
* The UI renders gracefully without crashing from unhandled API exceptions.

## Regression Tests
* Registration correctly creates users and personal workspaces using proper UUIDs.
* Network failures (e.g., disconnected backend) fall back to a safe "Failed to register" or `err.message` without white-screening.
* The `AppRouter` configuration was audited and confirmed healthy with proper `ErrorBoundary` protection at the `<App />` root level.
