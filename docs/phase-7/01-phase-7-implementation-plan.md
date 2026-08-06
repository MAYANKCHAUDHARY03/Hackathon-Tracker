# Phase 7 Implementation Plan

## Goal Description
Implement Phase 7: Search, Analytics, Import/Export, Public Portfolio, and Hardening for the Hackathon Tracker application. This transforms the platform into a discoverable, measurable, portable, and production-hardened system.

## Proposed Architecture & Strategy

### Stage 1 & 2: Search Foundation & Frontend
- **Backend Model:** We'll implement a `SearchService` that queries a set of normalized views or uses UNION ALL across entities (Hackathons, Projects, Teams, Tasks) to return a unified `SearchResultItem` matching the required schema. We will respect workspace boundaries. 
- **API Endpoint:** `GET /api/v1/workspaces/{workspace_id}/search?q=...&type=...`
- **Frontend:** Implement a global search bar in the `Topbar` or a dedicated search modal that debounces input, calls the search API, and renders categorized results with navigation links.

### Stage 3 & 4: Analytics Foundation & Frontend
- **Backend Model:** Implement an `AnalyticsService` to compute summary metrics: Active Hackathons, Tasks Completed, Submissions Ready, etc.
- **API Endpoint:** `GET /api/v1/workspaces/{workspace_id}/analytics?period=last_30_days`
- **Frontend:** Create an `Analytics.tsx` page to display metric cards. Integrate charts if a library exists, or use simple statistical progress bars. Add summary metrics to the existing `Dashboard.tsx`.

### Stage 5: Export and Import Foundation
- **Backend Models:** 
  - `GET /api/v1/workspaces/{workspace_id}/export`: Exports all workspace data as structured JSON.
  - `POST /api/v1/workspaces/{workspace_id}/import/preview`: Validates uploaded JSON.
  - `POST /api/v1/workspaces/{workspace_id}/import/execute`: Safely imports JSON data.
- **Frontend:** Add an Export/Import section in the Workspace `Settings.tsx` to download and upload workspace JSON data.

### Stage 6: Public Portfolio & Internal Profile
- **Backend Models:** Create `Portfolio` and `PortfolioItem` models linked to `User`.
- **API Endpoints:** `GET /api/v1/users/{user_id}/portfolio`, `PUT /api/v1/users/me/portfolio`.
- **Frontend:** Implement `Profile.tsx` for self-editing and `Portfolio.tsx` for public or internal display of user achievements and projects.

### Stage 7: Deployment & Security Hardening
- **Backend:** Enforce Rate Limiting (e.g., using `slowapi`), add security headers via middleware (e.g., `Secure-Headers`), validate all `.env` requirements on startup, ensure CORS settings are strictly bound to `settings.BACKEND_CORS_ORIGINS`.
- **Frontend:** Secure any remaining vulnerable React components against XSS, ensure all data fetching properly handles 401/403s.

## Validation & Testing Plan
- Write pytest cases for `test_search.py`, `test_analytics.py`, `test_export_import.py`, and `test_portfolio.py` ensuring isolation.
- E2E manual regression checking for correct routing from search, valid exports, and secure public/private boundaries.
