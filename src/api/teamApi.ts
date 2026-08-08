import { useWorkspaceStore } from '@/store/workspaceStore';

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

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token')}`
});

export const teamApi = {
  getTeams: async (workspaceId: string): Promise<Team[]> => {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/teams`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch teams');
    return res.json();
  },

  createTeam: async (workspaceId: string, data: Partial<Team>): Promise<Team> => {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/teams`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create team');
    return res.json();
  },

  updateTeam: async (workspaceId: string, teamId: string, data: Partial<Team>): Promise<Team> => {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/teams/${teamId}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update team');
    return res.json();
  },

  getTalentMatches: async (workspaceId: string, teamId: string): Promise<TalentMatch[]> => {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/teams/${teamId}/talent-matches`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch talent matches');
    return res.json();
  },

  applyToTeam: async (workspaceId: string, teamId: string): Promise<{status: string, message: string}> => {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/teams/${teamId}/apply`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to apply to team');
    return res.json();
  },

  inviteToTeam: async (workspaceId: string, teamId: string, personId: string): Promise<{status: string, message: string}> => {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/teams/${teamId}/invite/${personId}`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to invite to team');
    return res.json();
  }
};
