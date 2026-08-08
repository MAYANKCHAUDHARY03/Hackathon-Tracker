import { apiClient } from '../lib/api-client';

export interface ConnectorField {
  id: string;
  label: string;
  type: string;
  required: boolean;
}

export interface ConnectorInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  auth_type: string;
  config_schema: {
    fields: ConnectorField[];
  };
}

export interface WorkspaceIntegration {
  id: string;
  workspace_id: string;
  connector_id: string;
  name: string;
  is_active: boolean;
  config: Record<string, any>;
  last_sync_status?: string | null;
  last_sync_error?: string | null;
  created_at: string;
  updated_at: string;
}

export const hubIntegrationApi = {
  getConnectors: async (): Promise<ConnectorInfo[]> => {
    return await apiClient.get<ConnectorInfo[]>('/hub-integrations/connectors');
  },

  getWorkspaceIntegrations: async (workspaceId: string): Promise<WorkspaceIntegration[]> => {
    return await apiClient.get<WorkspaceIntegration[]>(`/hub-integrations/workspaces/${workspaceId}`);
  },

  createIntegration: async (data: { workspace_id: string; connector_id: string; name: string; is_active: boolean; config: Record<string, any> }): Promise<WorkspaceIntegration> => {
    return await apiClient.post<WorkspaceIntegration>('/hub-integrations/', data);
  },

  testIntegration: async (integrationId: string): Promise<{ status: string; error?: string }> => {
    return await apiClient.post<{ status: string; error?: string }>(`/hub-integrations/${integrationId}/test`, {});
  }
};
