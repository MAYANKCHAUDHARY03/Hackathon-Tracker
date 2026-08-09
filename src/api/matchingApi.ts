import { apiClient as api } from "@/lib/api-client";

export interface MatchResult {
  node_id: string;
  type: string;
  score: number;
  data: any;
}

export const matchingApi = {
  computeScore: (workspaceId: string, sourceId: string, targetId: string) =>
    api.post<{ score: number }>(`/workspaces/${workspaceId}/matching/score`, {
      source_id: sourceId,
      target_id: targetId
    }),
    
  findMatches: (workspaceId: string, sourceId: string, targetType: string, limit: number = 10) =>
    api.post<MatchResult[]>(`/workspaces/${workspaceId}/matching/find`, {
      source_id: sourceId,
      target_type: targetType,
      limit
    }),
};
