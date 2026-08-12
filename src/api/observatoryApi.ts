import { apiClient } from '@/lib/api-client'

export interface ObservatoryStats {
  total_projects: number
  total_participants: number
  total_hackathons: number
  total_jobs_created: number
  total_funding_raised: number
  total_revenue_generated: number
}

export const observatoryApi = {
  getWorkspaceStats: async (workspaceId: string): Promise<ObservatoryStats> => {
    return await apiClient.get<ObservatoryStats>(`/workspaces/${workspaceId}/observatory/stats`)
  }
}
