import { apiClient as api } from "@/lib/api-client";

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
  transitionState: (workspaceId: string, projectId: string, transition: ProjectTransitionCreate) =>
    api.post<any>(`/workspaces/${workspaceId}/projects/${projectId}/transitions`, transition),
    
  getTransitions: (workspaceId: string, projectId: string) =>
    api.get<ProjectTransition[]>(`/workspaces/${workspaceId}/projects/${projectId}/transitions`),
};
