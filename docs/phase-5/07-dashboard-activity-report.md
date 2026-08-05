# Stage 6: Dashboard and Activity Integration

## Implementation Details

We expanded the Dashboard to handle Action Items related to submission workflows and confirmed ActivityFeed integration.

### Components
- **Dashboard (`src/pages/Dashboard.tsx`)**: Appended an 'Action Items' section below the Upcoming Deadlines list. This panel surfaces immediate requirements for a team (like 'Complete Submission') based on current round progress.
- **ActivityFeed (`src/components/activity/ActivityFeed.tsx`)**: Audited to ensure that server-generated activities triggered by the backend during round updates or submission lock actions are correctly queried through `activityApi.getProjectActivities` and correctly rendered in real-time.

## Verification
- Running `npx tsc --noEmit` locally confirmed zero type errors across the newly introduced models and components.
- Dashboard renders correctly without errors, showing the new UI container for Action Items.

## Next Steps
Proceeding to Stages 7 & 8: End-to-End Verification and Final Polish.
