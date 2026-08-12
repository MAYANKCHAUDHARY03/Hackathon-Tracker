import { apiClient } from '@/lib/api-client';

export interface TrustVerification {
  id: string;
  workspace_id: string;
  entity_type: string;
  entity_id: string;
  achievement_type: string;
  achievement_detail: string;
  source?: string;
  status: 'pending' | 'verified' | 'rejected';
  verifier_id?: string;
  verified_at?: string;
  created_at: string;
  updated_at: string;
}

export interface VerificationCreate {
  entity_type: string;
  entity_id: string;
  achievement_type: string;
  achievement_detail: string;
  source?: string;
}

export const verificationApi = {
  getVerifications: async (workspaceId: string): Promise<TrustVerification[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/verifications`);
    return response as any as TrustVerification[];
  },

  requestVerification: async (workspaceId: string, data: VerificationCreate): Promise<TrustVerification> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/verifications`, data);
    return response as any as TrustVerification;
  },

  verifyAchievement: async (workspaceId: string, verificationId: string): Promise<TrustVerification> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/verifications/${verificationId}/verify`, null);
    return response as any as TrustVerification;
  },

  rejectAchievement: async (workspaceId: string, verificationId: string): Promise<TrustVerification> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/verifications/${verificationId}/reject`, null);
    return response as any as TrustVerification;
  }
};
