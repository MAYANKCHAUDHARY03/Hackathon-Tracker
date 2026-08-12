import { apiClient } from '@/lib/api-client';

export interface PortfolioCreate {
  name: string;
  description?: string;
  is_public?: boolean;
}

export interface PortfolioResponse {
  id: string;
  workspace_id: string;
  owner_id: string;
  owner_type: string;
  name: string;
  description?: string;
  is_public: boolean;
  projects?: any[]; // We can refine this type based on the backend response
  created_at: string;
  updated_at: string;
}

export interface PortfolioProjectAdd {
  project_id: string;
}

export const crossPortfolioApi = {
  createPortfolio: async (workspaceId: string, data: PortfolioCreate): Promise<PortfolioResponse> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/portfolios`, data);
    return response as any as PortfolioResponse;
  },

  listPortfolios: async (workspaceId: string): Promise<PortfolioResponse[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/portfolios`);
    return response as any as PortfolioResponse[];
  },

  addProjectToPortfolio: async (workspaceId: string, portfolioId: string, data: PortfolioProjectAdd): Promise<PortfolioResponse> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/portfolios/${portfolioId}/projects`, data);
    return response as any as PortfolioResponse;
  }
};
