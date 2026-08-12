import { apiClient as api } from '@/lib/api-client';

export interface Team {
  id: string;
  name: string;
  hackathon_id: string;
  description?: string;
  skills_needed?: string[];
  status: string;
  workspace_id: string;
  created_at: string;
  updated_at: string;
}

export interface TalentMatch {
  person_id: string;
  full_name: string;
  designation?: string;
  expertise_areas?: string[];
  match_score: number;
}

export const teamApi = {
  getTeams: (workspaceId: string) =>
    api.get<Team[]>(`/workspaces/${workspaceId}/teams`),

  createTeam: (workspaceId: string, data: Partial<Team>) =>
    api.post<Team>(`/workspaces/${workspaceId}/teams`, data),

  updateTeam: (workspaceId: string, teamId: string, data: Partial<Team>) =>
    api.patch<Team>(`/workspaces/${workspaceId}/teams/${teamId}`, data),

  getTalentMatches: (workspaceId: string, teamId: string) =>
    api.get<TalentMatch[]>(`/workspaces/${workspaceId}/teams/${teamId}/talent-matches`),

  applyToTeam: (workspaceId: string, teamId: string) =>
    api.post<{status: string, message: string}>(`/workspaces/${workspaceId}/teams/${teamId}/apply`, {}),

  inviteToTeam: (workspaceId: string, teamId: string, personId: string) =>
    api.post<{status: string, message: string}>(`/workspaces/${workspaceId}/teams/${teamId}/invite/${personId}`, {})
};
