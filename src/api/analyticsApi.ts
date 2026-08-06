import { apiClient as api } from "@/lib/api-client";

export interface WorkspaceAnalyticsSummary {
  total_hackathons: number;
  active_hackathons: number;
  total_projects: number;
  total_teams: number;
  total_users: number;
  tasks_completed: number;
  tasks_pending: number;
  recent_activity_count: number;
  metadata: Record<string, any>;
}

export const analyticsApi = {
  getWorkspaceAnalytics: (workspaceId: string) =>
    api.get<WorkspaceAnalyticsSummary>(`/workspaces/${workspaceId}/analytics`),
};
