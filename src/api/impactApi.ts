import { apiClient } from '@/lib/api-client';

export interface FunnelMetrics {
  participation: number;
  projects: number;
  prototypes: number;
  pilots: number;
  deployments: number;
  startups: number;
  jobs: number;
}

export interface CustomMetric {
  id: string;
  name: string;
  description?: string;
  unit: string;
}

export interface ProjectImpact {
  id: string;
  project_id: string;
  stage: string;
  custom_metrics: Record<string, number>;
  jobs_created: number;
  funding_raised: number;
  revenue_generated: number;
}

export const impactApi = {
  getFunnelMetrics: async (workspaceId: string): Promise<FunnelMetrics> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/impact/funnel`);
    return response as any as FunnelMetrics;
  },

  getCustomMetrics: async (workspaceId: string): Promise<CustomMetric[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/impact/metrics`);
    return response as any as CustomMetric[];
  },

  createCustomMetric: async (workspaceId: string, metric: Partial<CustomMetric>): Promise<CustomMetric> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/impact/metrics`, metric);
    return response as any as CustomMetric;
  },

  getProjectImpacts: async (workspaceId: string): Promise<ProjectImpact[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/impact/projects`);
    return response as any as ProjectImpact[];
  },

  updateProjectImpact: async (workspaceId: string, projectId: string, impact: Partial<ProjectImpact>): Promise<ProjectImpact> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/impact/projects/${projectId}`, impact);
    return response as any as ProjectImpact;
  }
};
