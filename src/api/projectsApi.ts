import { apiClient as api } from "@/lib/api-client";
import type { Project } from "@/types";

export interface ProjectTransition {
  state: string;
  transitioned_at: string;
  actor_id: string;
  actor_name: string;
  notes?: string;
}

export interface ProjectTransitionCreate {
  state: string;
  notes?: string;
}

export const projectsApi = {
  getProjects: (workspaceId: string) => {
    if (!workspaceId || workspaceId === 'undefined' || workspaceId === 'null') {
      return Promise.resolve([]);
    }
    return api.get<Project[]>(`/workspaces/${workspaceId}/projects`);
  },

  createProject: (workspaceId: string, teamId: string, data: Partial<Project>) =>
    api.post<Project>(`/workspaces/${workspaceId}/teams/${teamId}/projects`, data),

  transitionState: (workspaceId: string, projectId: string, transition: ProjectTransitionCreate) =>
    api.post<any>(`/workspaces/${workspaceId}/projects/${projectId}/transitions`, transition),
    
  getTransitions: (workspaceId: string, projectId: string) =>
    api.get<ProjectTransition[]>(`/workspaces/${workspaceId}/projects/${projectId}/transitions`),
};
