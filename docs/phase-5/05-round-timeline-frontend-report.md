# Stage 4: Frontend State and Services Report

## Implementation Details

We have extended the React frontend to support fetching and rendering Rounds and Deadlines associated with Hackathons, providing the foundation for team submissions.

### API Integration
- Created `src/api/roundApi.ts` mapping to backend round endpoints.
- Created `src/api/submissionApi.ts` mapping to backend submission and requirements endpoints.

### User Interface Components
- Implemented `src/pages/HackathonDetails.tsx` as the main view for a specific Hackathon. It pulls Hackathon data from `useHackathonStore` and fetches specific rounds and deadlines via the new API clients.
- Created `src/pages/Calendar.tsx` as a placeholder for the future global schedule view.
- Added both components to `src/router/index.tsx` mapping `/hackathons/:id` to the details page and `/calendar` to the calendar feature.

## Verification
- Running `npx tsc --noEmit` locally confirmed zero type errors across the newly introduced models and components.
- The UI properly gracefully handles missing data scenarios and leverages existing UI components (e.g. `GlassPanel`).

## Next Steps
Proceeding to Stage 5: Submission Upload & State Workflow where teams will be able to perform submission data entry and lock their forms.
