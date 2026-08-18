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
    return await apiClient.get<WorkspacePolicy>(`/workspaces/${workspaceId}/governance/policy`);
  },

  updatePolicy: async (workspaceId: string, data: WorkspacePolicy): Promise<WorkspacePolicy> => {
    return await apiClient.put<WorkspacePolicy>(`/workspaces/${workspaceId}/governance/policy`, data);
  },

  getDSRs: async (workspaceId: string): Promise<DSR[]> => {
    return await apiClient.get<DSR[]>(`/workspaces/${workspaceId}/governance/dsr`);
  },

  updateDSRStatus: async (workspaceId: string, dsrId: string, status: string, resolution_notes: string): Promise<DSR> => {
    return await apiClient.put<DSR>(`/workspaces/${workspaceId}/governance/dsr/${dsrId}/status`, {
      status,
      resolution_notes,
    });
  },

  getAuditLogs: async (workspaceId: string): Promise<AuditLog[]> => {
    return await apiClient.get<AuditLog[]>(`/workspaces/${workspaceId}/governance/audit`);
  },
};
