import { apiClient } from '../lib/api-client';

export interface APIKey {
  id: string;
  name: string;
  prefix: string;
  scopes: string[];
  expires_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
  created_at: string;
}

export interface APIKeyCreateResponse extends APIKey {
  key: string; // The raw unhashed key
}

export interface APIKeyCreate {
  name: string;
  scopes?: string[];
  expires_at?: string | null;
}

export const apiKeyApi = {
  listAPIKeys: async (workspaceId: string): Promise<APIKey[]> => {
    return await apiClient.get<APIKey[]>(`/workspaces/${workspaceId}/api-keys`);
  },

  createAPIKey: async (workspaceId: string, data: APIKeyCreate): Promise<APIKeyCreateResponse> => {
    return await apiClient.post<APIKeyCreateResponse>(`/workspaces/${workspaceId}/api-keys`, data);
  },

  revokeAPIKey: async (workspaceId: string, keyId: string): Promise<void> => {
    await apiClient.delete(`/workspaces/${workspaceId}/api-keys/${keyId}`);
  }
};
