import { apiClient as api } from "@/lib/api-client";
import type { Hackathon } from "@/types";

export const hackathonApi = {
  getHackathons: (workspaceId: string) => {
    if (!workspaceId || workspaceId === 'undefined' || workspaceId === 'null') {
      return Promise.resolve([]);
    }
    return api.get<Hackathon[]>(`/workspaces/${workspaceId}/hackathons`);
  },

  createHackathon: (workspaceId: string, data: Partial<Hackathon>) =>
    api.post<Hackathon>(`/workspaces/${workspaceId}/hackathons`, data),

  getHackathon: (workspaceId: string, id: string) =>
    api.get<Hackathon>(`/workspaces/${workspaceId}/hackathons/${id}`),

  getRounds: (workspaceId: string, hackathonId: string) =>
    api.get<any[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/rounds`),

  updateHackathon: (workspaceId: string, id: string, data: Partial<Hackathon>) =>
    api.put<Hackathon>(`/workspaces/${workspaceId}/hackathons/${id}`, data),
};
