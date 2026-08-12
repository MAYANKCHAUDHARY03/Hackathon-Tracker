import { apiClient } from '@/lib/api-client';

export interface CopilotQuery {
  query: string;
}

export interface SourceEntity {
  id: string;
  type: string;
  name: string;
}

export interface CopilotResponse {
  answer: string;
  evidence: string[];
  source_entities: SourceEntity[];
  confidence: number;
  recommended_action?: string;
}

export const copilotApi = {
  ask: async (workspaceId: string, query: string): Promise<CopilotResponse> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/copilot/ask`, { query });
    return response as any as CopilotResponse;
  },
};
