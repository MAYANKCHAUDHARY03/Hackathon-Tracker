import { apiClient } from '../lib/api-client';

export interface ResearchLink {
  id: string;
  workspace_id: string;
  project_id: string;
  type: string; // paper, patent, dataset, repo, institution
  title: string;
  url?: string;
  identifier?: string;
  authors?: string[];
  publication_date?: string;
  provenance: string; // user-provided, AI-inferred
  created_at: string;
  updated_at: string;
}

export interface ResearchLinkCreate {
  project_id: string;
  type: string;
  title: string;
  url?: string;
  identifier?: string;
  authors?: string[];
  publication_date?: string;
}

export const researchApi = {
  getLinks: async (workspaceId: string, projectId: string) => {
    return await apiClient.get<ResearchLink[]>(`/workspaces/${workspaceId}/research/project/${projectId}`);
  },
  
  createLink: async (workspaceId: string, data: ResearchLinkCreate) => {
    return await apiClient.post<ResearchLink>(`/workspaces/${workspaceId}/research/`, data);
  },
  
  deleteLink: async (workspaceId: string, linkId: string) => {
    return await apiClient.delete(`/workspaces/${workspaceId}/research/${linkId}`);
  }
};
