import { apiClient } from '@/lib/api-client';

export interface AutomationRuleBase {
  name: string;
  description?: string;
  trigger_type: string;
  action_type: string;
  conditions: Record<string, any>;
  enabled?: boolean;
}

export interface AutomationRuleCreate extends AutomationRuleBase {
  organization_id?: string;
  workspace_id?: string;
}

export interface AutomationRuleUpdate {
  name?: string;
  description?: string;
  trigger_type?: string;
  action_type?: string;
  conditions?: Record<string, any>;
  enabled?: boolean;
}

export interface AutomationRuleResponse extends AutomationRuleBase {
  id: string;
  organization_id: string;
  workspace_id?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  archived_at?: string;
}

export interface AutomationExecutionResponse {
  id: string;
  rule_id: string;
  triggering_event: Record<string, any>;
  status: string;
  attempts: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
  correlation_id?: string;
  created_at: string;
  updated_at: string;
}

export const automationApi = {
  listRules: async (workspaceId: string): Promise<AutomationRuleResponse[]> => {
    return apiClient.get(`/workspaces/${workspaceId}/automation/rules`);
  },

  createRule: async (workspaceId: string, rule: AutomationRuleCreate): Promise<AutomationRuleResponse> => {
    return apiClient.post(`/workspaces/${workspaceId}/automation/rules`, rule);
  },

  getRule: async (workspaceId: string, ruleId: string): Promise<AutomationRuleResponse> => {
    return apiClient.get(`/workspaces/${workspaceId}/automation/rules/${ruleId}`);
  },

  updateRule: async (workspaceId: string, ruleId: string, updates: AutomationRuleUpdate): Promise<AutomationRuleResponse> => {
    return apiClient.put(`/workspaces/${workspaceId}/automation/rules/${ruleId}`, updates);
  },

  deleteRule: async (workspaceId: string, ruleId: string): Promise<void> => {
    return apiClient.delete(`/workspaces/${workspaceId}/automation/rules/${ruleId}`);
  },

  listRuleExecutions: async (workspaceId: string, ruleId: string): Promise<AutomationExecutionResponse[]> => {
    return apiClient.get(`/workspaces/${workspaceId}/automation/rules/${ruleId}/executions`);
  }
};
