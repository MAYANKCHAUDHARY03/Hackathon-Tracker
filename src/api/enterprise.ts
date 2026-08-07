import { apiClient } from '../lib/api-client';

export interface HealthResponse {
  status: string;
  services: {
    database: string;
    api: string;
  };
}

export interface MetricsResponse {
  system_cpu_usage_percent: number;
  system_memory_usage_percent: number;
  system_memory_available_bytes: number;
}

export const enterpriseApi = {
  getHealth: () => apiClient.get<HealthResponse>('/ops/health'),
  getMetrics: () => apiClient.get<MetricsResponse>('/ops/metrics'),
  generateScimToken: (workspaceId: string) => apiClient.post<{ token: string }>(`/workspaces/${workspaceId}/scim/token`, {}),
  getOidcProviders: (workspaceId: string) => apiClient.get<any[]>(`/workspaces/${workspaceId}/identity-providers`),
  createOidcProvider: (workspaceId: string, data: any) => apiClient.post<any>(`/workspaces/${workspaceId}/identity-providers`, data),
};
