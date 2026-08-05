import type { ID, ISO8601Date } from './index';

export interface DashboardHackathonItem {
  id: ID;
  name: string;
  status: string;
  start_date: ISO8601Date;
  end_date: ISO8601Date;
  registration_deadline: ISO8601Date;
  updated_at: ISO8601Date;
}

export interface DashboardSummaryResponse {
  total_active: number;
  total_upcoming: number;
  total_completed: number;
  total_non_archived: number;
  upcoming_deadlines: DashboardHackathonItem[];
  nearest_upcoming_event: DashboardHackathonItem | null;
  recently_updated: DashboardHackathonItem[];
}
