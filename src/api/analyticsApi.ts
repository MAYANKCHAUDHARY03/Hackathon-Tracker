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

export interface AnalyticsOverview {
  total_users: number;
  total_teams: number;
  total_projects: number;
  total_submissions: number;
}

export interface AnalyticsDemographics {
  skills_distribution: Record<string, number>;
  roles_distribution: Record<string, number>;
}

export interface ScoreDistribution {
  range_0_20: number;
  range_21_40: number;
  range_41_60: number;
  range_61_80: number;
  range_81_100: number;
}

export interface AnalyticsEvaluations {
  average_score: number;
  total_evaluations: number;
  score_distribution: ScoreDistribution;
}

export const analyticsApi = {
  getWorkspaceAnalytics: (workspaceId: string) =>
    api.get<WorkspaceAnalyticsSummary>(`/workspaces/${workspaceId}/analytics`),
  getOverview: (workspaceId: string) =>
    api.get<AnalyticsOverview>(`/analytics/workspaces/${workspaceId}/analytics/overview`),
  getDemographics: (workspaceId: string) =>
    api.get<AnalyticsDemographics>(`/analytics/workspaces/${workspaceId}/analytics/demographics`),
  getEvaluations: (workspaceId: string) =>
    api.get<AnalyticsEvaluations>(`/analytics/workspaces/${workspaceId}/analytics/evaluations`),
};
