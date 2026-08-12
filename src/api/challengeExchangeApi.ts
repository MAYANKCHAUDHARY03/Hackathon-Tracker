import { apiClient } from '../lib/api-client';

export interface Problem {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  domain?: string;
  status: string;
}

export interface Challenge {
  id: string;
  workspace_id: string;
  hackathon_id?: string;
  problem_id?: string;
  title: string;
  slug: string;
  description?: string;
  category?: string;
  domain?: string;
  difficulty?: string;
  visibility: string;
  submission_count: number;
  status: string;
  created_at: string;
  problem?: Problem;
}

export const challengeExchangeApi = {
  listProblems: async (
    workspaceId: string,
    params?: { domain?: string; status?: string; limit?: number; offset?: number }
  ) => {
    const searchParams = new URLSearchParams({ workspace_id: workspaceId });
    if (params?.domain) searchParams.append('domain', params.domain);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());
    
    return await apiClient.get<{ problems: Problem[] }>(`/challenge-exchange/problems?${searchParams}`);
  },

  browseChallenges: async (
    workspaceId: string,
    params?: { category?: string; domain?: string; difficulty?: string; search_term?: string; limit?: number; offset?: number }
  ) => {
    const searchParams = new URLSearchParams({ workspace_id: workspaceId });
    if (params?.category) searchParams.append('category', params.category);
    if (params?.domain) searchParams.append('domain', params.domain);
    if (params?.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params?.search_term) searchParams.append('search_term', params.search_term);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());

    return await apiClient.get<{ challenges: Challenge[] }>(`/challenge-exchange/challenges?${searchParams}`);
  },

  expressInterest: async (workspaceId: string, challengeId: string) => {
    return await apiClient.post<{ status: string }>(`/challenge-exchange/challenges/${challengeId}/interest?workspace_id=${workspaceId}`, {});
  }
};
