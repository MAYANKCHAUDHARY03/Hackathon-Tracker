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
    const res = await apiClient.post(`/workspaces/${workspaceId}/developer/apps`, data);
    return res.data;
  },
  
  getApps: async (workspaceId: string): Promise<DeveloperApp[]> => {
    const res = await apiClient.get(`/workspaces/${workspaceId}/developer/apps`);
    return res.data;
  }
};
