import { apiClient as api } from "@/lib/api-client";
import type { Hackathon } from "@/types";

export const hackathonApi = {
  getHackathons: (workspaceId: string) =>
    api.get<Hackathon[]>(`/workspaces/${workspaceId}/hackathons`),

  createHackathon: (workspaceId: string, data: Partial<Hackathon>) =>
    api.post<Hackathon>(`/workspaces/${workspaceId}/hackathons`, data),

  getHackathon: (id: string) =>
    api.get<Hackathon>(`/hackathons/${id}`),

  updateHackathon: (id: string, data: Partial<Hackathon>) =>
    api.patch<Hackathon>(`/hackathons/${id}`, data),
};
