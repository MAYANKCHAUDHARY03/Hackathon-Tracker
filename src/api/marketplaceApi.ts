import { apiClient as api } from "@/lib/api-client";

export interface MarketplaceProject {
  id: string;
  title: string;
  slug: string;
  status: string;
  description?: string;
  technologies: string[];
  hackathon_origin?: string;
}

export interface MarketplacePartner {
  id: string;
  type: string;
  name: string;
  description?: string;
  resources_offered: string[];
}

export interface MarketplaceProjectsResponse {
  projects: MarketplaceProject[];
}

export interface MarketplacePartnersResponse {
  partners: MarketplacePartner[];
}

export const marketplaceApi = {
  getProjects: async (workspaceId: string): Promise<MarketplaceProjectsResponse> => {
    return await api.get<MarketplaceProjectsResponse>(`/marketplace/projects?workspace_id=${workspaceId}`);
  },

  getPartners: async (workspaceId: string): Promise<MarketplacePartnersResponse> => {
    return await api.get<MarketplacePartnersResponse>(`/marketplace/partners?workspace_id=${workspaceId}`);
  },
};
