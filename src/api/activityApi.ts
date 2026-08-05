import { apiClient } from '@/lib/api-client';

export interface ActivityEvent {
  id: string;
  workspace_id: string;
  project_id?: string;
  user_id: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  safe_metadata?: Record<string, any>;
  created_at: string;
}

export const activityApi = {
  getProjectActivities: (workspaceId: string, projectId: string) =>
    apiClient.get<ActivityEvent[]>(`/workspaces/${workspaceId}/projects/${projectId}/activities`),
};
