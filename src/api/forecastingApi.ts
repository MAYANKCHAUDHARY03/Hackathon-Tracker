import { apiClient } from '@/lib/api-client';

export interface ForecastResponse {
  id: string;
  target_type: string;
  target_id: string;
  forecast_type: string;
  prediction: Record<string, any>;
  confidence: number;
  factors: string[];
  is_prediction: boolean;
  created_at: string;
}

export const forecastingApi = {
  generateProjectForecast: async (workspaceId: string, projectId: string): Promise<ForecastResponse> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/forecasting/projects/${projectId}`);
    return response as any as ForecastResponse;
  },
};
