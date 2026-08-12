import { apiClient } from '@/lib/api-client';

export interface MatchProfileCreate {
  entity_type: string;
  entity_id: string;
  looking_for: string[];
  tags: string[];
}

export interface MatchProfileResponse extends MatchProfileCreate {
  id: string;
  workspace_id: string;
  created_at: string;
  updated_at: string;
}

export interface MatchOpportunityCreate {
  type: string;
  title: string;
  description?: string;
  tags: string[];
}

export interface MatchOpportunityResponse extends MatchOpportunityCreate {
  id: string;
  workspace_id: string;
  provider_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface MatchRecommendationResponse {
  id: string;
  profile_id: string;
  opportunity: MatchOpportunityResponse;
  score: number;
  reason?: string;
  created_at: string;
}

export const matchmakingApi = {
  createProfile: async (workspaceId: string, profile: MatchProfileCreate): Promise<MatchProfileResponse> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/matchmaking/profiles`, profile);
    return response as any as MatchProfileResponse;
  },

  createOpportunity: async (workspaceId: string, opportunity: MatchOpportunityCreate): Promise<MatchOpportunityResponse> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/matchmaking/opportunities`, opportunity);
    return response as any as MatchOpportunityResponse;
  },

  listOpportunities: async (workspaceId: string): Promise<MatchOpportunityResponse[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/matchmaking/opportunities`);
    return response as any as MatchOpportunityResponse[];
  },

  generateRecommendations: async (workspaceId: string, profileId: string): Promise<MatchRecommendationResponse[]> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/matchmaking/profiles/${profileId}/recommendations`, null);
    return response as any as MatchRecommendationResponse[];
  }
};
