import { apiClient } from '../lib/api-client';

export interface AgentApprovalRequest {
  id: string;
  workspace_id: string;
  agent_name: string;
  tool_name: string;
  parameters_json: Record<string, any>;
  risk_level: string;
  status: 'pending' | 'approved' | 'rejected' | 'failed' | 'executed';
  requested_at: string;
  justification?: string;
  resolved_by_id?: string;
  resolved_at?: string;
}

export const agentApprovalApi = {
  getPendingApprovals: async (): Promise<AgentApprovalRequest[]> => {
    return await apiClient.get<AgentApprovalRequest[]>('/approvals');
  },

  approveRequest: async (approvalId: string): Promise<any> => {
    return await apiClient.post(`/approvals/${approvalId}/approve`);
  },

  rejectRequest: async (approvalId: string): Promise<any> => {
    return await apiClient.post(`/approvals/${approvalId}/reject`);
  },
};
