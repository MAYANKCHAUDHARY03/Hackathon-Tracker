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

  getHackathon: (id: string) =>
    api.get<Hackathon>(`/hackathons/${id}`),

  getRounds: (hackathonId: string) =>
    api.get<any[]>(`/hackathons/${hackathonId}/rounds`),

  updateHackathon: (id: string, data: Partial<Hackathon>) =>
    api.patch<Hackathon>(`/hackathons/${id}`, data),
};
