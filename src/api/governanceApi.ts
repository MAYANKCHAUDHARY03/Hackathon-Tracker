import { apiClient } from '../lib/api-client';

export interface WorkspacePolicy {
  data_residency: string;
  retention_days: number;
  ai_consent: boolean;
}

export interface DSR {
  id: string;
  workspace_id: string;
  user_id: string;
  request_type: 'export' | 'deletion' | 'rectification';
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  details?: string;
  resolution_notes?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  workspace_id: string;
  actor_id?: string;
  action: string;
  target_resource?: string;
  target_id?: string;
  details?: any;
  ip_address?: string;
  created_at: string;
}

export const governanceApi = {
  getPolicy: async (workspaceId: string): Promise<WorkspacePolicy> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/governance/policy`);
    return response.data;
  },

  updatePolicy: async (workspaceId: string, data: WorkspacePolicy): Promise<WorkspacePolicy> => {
    const response = await apiClient.put(`/workspaces/${workspaceId}/governance/policy`, data);
    return response.data;
  },

  getDSRs: async (workspaceId: string): Promise<DSR[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/governance/dsr`);
    return response.data;
  },

  updateDSRStatus: async (workspaceId: string, dsrId: string, status: string, resolution_notes: string): Promise<DSR> => {
    const response = await apiClient.put(`/workspaces/${workspaceId}/governance/dsr/${dsrId}/status`, {
      status,
      resolution_notes,
    });
    return response.data;
  },

  getAuditLogs: async (workspaceId: string): Promise<AuditLog[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/governance/audit`);
    return response.data;
  },
};
