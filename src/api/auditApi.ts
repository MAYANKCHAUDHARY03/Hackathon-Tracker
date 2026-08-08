import { apiClient } from '../lib/api-client';

export interface AuditLog {
  id: string;
  workspace_id: string;
  actor_id?: string;
  action: string;
  resource_type: string;
  resource_id: string;
  metadata_json?: Record<string, any>;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLog[];
  total: number;
}

export const auditApi = {
  getAuditLogs: (workspaceId: string, skip: number = 0, limit: number = 50) =>
    apiClient.get<AuditLogListResponse>(`/workspaces/${workspaceId}/audit-logs?skip=${skip}&limit=${limit}`),
};
