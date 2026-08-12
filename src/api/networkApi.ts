import { apiClient } from '../lib/api-client';

export interface NetworkResolveRequest {
  query: string;
  target_type?: string;
  include_impact_metrics?: boolean;
}

export interface NetworkNode {
  id: string;
  type: string;
  name: string;
  metadata: Record<string, any>;
}

export interface NetworkEdge {
  source: string;
  target: string;
  relation: string;
}

export interface NetworkResolveResponse {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  ai_summary?: string;
}

export const networkApi = {
  resolveNetwork: async (workspaceId: string, request: NetworkResolveRequest): Promise<NetworkResolveResponse> => {
    const response = await apiClient.post<NetworkResolveResponse>(`/workspaces/${workspaceId}/network/resolve`, request);
    return response;
  },
};
