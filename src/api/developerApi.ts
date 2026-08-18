import { apiClient } from '../lib/api-client';

export interface DeveloperApp {
  id: string;
  workspace_id: string;
  name: string;
  client_id: string;
  client_secret: string;
  redirect_uris: string[];
  created_at: string;
  updated_at: string;
}

export interface DeveloperAppCreate {
  name: string;
  redirect_uris: string[];
}

export const developerApi = {
  createApp: async (workspaceId: string, data: DeveloperAppCreate): Promise<DeveloperApp> => {
    return await apiClient.post<DeveloperApp>(`/workspaces/${workspaceId}/developer/apps`, data);
  },
  
  getApps: async (workspaceId: string): Promise<DeveloperApp[]> => {
    return await apiClient.get<DeveloperApp[]>(`/workspaces/${workspaceId}/developer/apps`);
  }
};
