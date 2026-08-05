import { apiClient as api } from "@/lib/api-client";

export interface HackathonResult {
  id: string;
  hackathon_id: string;
  team_id: string;
  project_id?: string;
  round_id?: string;
  result_type: string;
  position?: number;
  title: string;
  description?: string;
  status: string;
  announced_at?: string;
  source_url?: string;
  is_verified: boolean;
  verification_note?: string;
}

export interface Reward {
  id: string;
  hackathon_id: string;
  team_id?: string;
  result_id?: string;
  title: string;
  reward_type: string;
  monetary_value?: number;
  currency?: string;
  sponsor?: string;
  description?: string;
  status: string;
  received_at?: string;
}

export interface Achievement {
  id: string;
  user_id?: string;
  team_id?: string;
  hackathon_id: string;
  project_id?: string;
  result_id?: string;
  achievement_type: string;
  title: string;
  description?: string;
  achieved_at: string;
  visibility: string;
  source?: string;
}

export const outcomesApi = {
  getResults: (workspaceId: string, hackathonId: string) =>
    api.get<HackathonResult[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/results`),

  createResult: (workspaceId: string, hackathonId: string, data: Partial<HackathonResult>) =>
    api.post<HackathonResult>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/results`, data),

  getRewards: (workspaceId: string, hackathonId: string) =>
    api.get<Reward[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/rewards`),

  createReward: (workspaceId: string, hackathonId: string, data: Partial<Reward>) =>
    api.post<Reward>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/rewards`, data),

  getAchievements: (workspaceId: string, hackathonId: string) =>
    api.get<Achievement[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/achievements`),

  createAchievement: (workspaceId: string, hackathonId: string, data: Partial<Achievement>) =>
    api.post<Achievement>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/achievements`, data),
};
