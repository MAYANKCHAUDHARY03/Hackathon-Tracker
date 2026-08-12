import { apiClient } from '@/lib/api-client'

export interface FederationLink {
  id: string
  source_workspace_id: string
  target_workspace_id: string
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'REVOKED'
  shared_entities: string[]
  created_at: string
  updated_at: string
}

export interface CreateFederationRequest {
  target_workspace_id: string
  shared_entities?: string[]
}

export const federationApi = {
  getLinks: async (workspaceId: string): Promise<FederationLink[]> => {
    return await apiClient.get<FederationLink[]>(`/workspaces/${workspaceId}/federation`)
  },
  
  createLink: async (workspaceId: string, data: CreateFederationRequest): Promise<FederationLink> => {
    return await apiClient.post<FederationLink>(`/workspaces/${workspaceId}/federation`, data)
  },

  updateLinkStatus: async (workspaceId: string, linkId: string, status: string): Promise<FederationLink> => {
    return await apiClient.put<FederationLink>(`/workspaces/${workspaceId}/federation/${linkId}`, { status })
  }
}
