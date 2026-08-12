# Phase 39: Impact Measurement

**Status:** Completed

## Objective
Implement a system to track long-term ROI and impact metrics for hackathon projects, ensuring that standard funnel metrics and custom workspace-specific metrics can be measured.

## Key Accomplishments

### Backend
1. **Impact Service & Router**: 
   - Created `/api/v1/workspaces/{workspace_id}/impact/funnel` endpoint to dynamically calculate the project funnel (Participation -> Projects -> Prototypes -> Pilots -> Deployments -> Startups).
   - Created `/projects` and `/projects/{project_id}` endpoints to list and update the funnel stage and specific impact metrics (jobs created, funding raised, revenue generated) of projects.
   - Created `/metrics` endpoints to define and list custom impact metrics for the workspace (e.g., "$ saved", "hours saved", "kg CO2").
2. **Schema & Model**:
   - Validated that `CustomMetric` and `ProjectImpact` database models and schemas are properly implemented and connected to SQLAlchemy.
   - Applied missing tables to the SQLite database via a custom python initialization script.

### Frontend
1. **Impact API Client**:
   - Added `src/api/impactApi.ts` to connect the frontend to the new backend endpoints.
2. **Impact Measurement Dashboard (`src/pages/ImpactMeasurement.tsx`)**:
   - Built a comprehensive dashboard displaying the funnel metrics dynamically.
   - Implemented a form to update individual project funnel stages and report core metrics like Jobs Created, Funding Raised, and Revenue Generated.
   - Added a section to define and manage Custom Metrics for the workspace.
3. **Routing & Navigation**:
   - Registered the `ImpactMeasurement` component in `src/router/index.tsx`.
   - Added the "Impact Measurement" link to the primary sidebar in `src/components/layout/Sidebar.tsx` with a `Target` icon.

## Next Steps
- Implement Phase 40: Ecosystem Observatory.
