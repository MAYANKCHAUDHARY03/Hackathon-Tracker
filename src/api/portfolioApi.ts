import { apiClient as api } from "@/lib/api-client";

export interface PortfolioItem {
  id: string;
  name: string;
  description?: string;
  type: string;
  url?: string;
  date: string;
}

export interface UserPortfolio {
  user_id: string;
  full_name: string;
  bio?: string;
  items: PortfolioItem[];
}

export interface OrgPortfolioStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  startups_spawned: number;
  patents_research: number;
  top_technologies: string[];
}

export interface OrgPortfolioProject {
  id: string;
  name: string;
  status: string;
  technologies: string[];
  description?: string;
}

export interface OrganizationPortfolio {
  org_id: string;
  name: string;
  stats: OrgPortfolioStats;
  projects: OrgPortfolioProject[];
  startups: any[];
}

export interface TechnologyCount {
  name: string;
  count: number;
}

export interface WorkspacePortfolioMetrics {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  startups_spawned: number;
  patents_filed: number;
  top_technologies: TechnologyCount[];
  total_participants: number;
}

export const portfolioApi = {
  getUserPortfolio: (userId: string) =>
    api.get<UserPortfolio>(`/users/${userId}/portfolio`),
    
  getOrganizationPortfolio: (workspaceId: string, orgId: string) =>
    api.get<OrganizationPortfolio>(`/workspaces/${workspaceId}/organizations/${orgId}/portfolio`),
    
  getWorkspacePortfolio: (workspaceId: string) =>
    api.get<WorkspacePortfolioMetrics>(`/workspaces/${workspaceId}/portfolio`),
};

