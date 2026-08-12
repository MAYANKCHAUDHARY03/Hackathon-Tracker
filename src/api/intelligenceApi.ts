import { apiClient as api } from "@/lib/api-client";

export interface TechnologyAdoptionMetric {
  technology_name: string;
  category: string;
  project_count: number;
}

export interface ProjectStatusMetric {
  status: string;
  project_count: number;
}

export interface ParticipationTrendMetric {
  period: string;
  project_count: number;
}

export interface EcosystemAnalyticsResponse {
  total_projects: number;
  total_technologies: number;
  top_technologies: TechnologyAdoptionMetric[];
  project_status_distribution: ProjectStatusMetric[];
  participation_trends: ParticipationTrendMetric[];
}

export const intelligenceApi = {
  getEcosystemAnalytics: async (): Promise<EcosystemAnalyticsResponse> => {
    const response = await api.get('/intelligence/ecosystem');
    return response as any as EcosystemAnalyticsResponse;
  }
};
