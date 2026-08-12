import { apiClient as api } from "@/lib/api-client";

export interface ProjectUpdate {
  id: string;
  project_id: string;
  author_id?: string;
  created_at: string;
  title: string;
  content: string;
  update_type: 'progress_report' | 'investor_update' | 'kpi';
  kpi_metrics?: Record<string, any>;
}

export interface ProjectDocument {
  id: string;
  project_id: string;
  uploaded_by_id?: string;
  created_at: string;
  title: string;
  document_type: 'business_plan' | 'pitch_deck' | 'legal' | 'financial' | 'other';
  url: string;
}

export interface ProjectFunding {
  id: string;
  project_id: string;
  created_at: string;
  round_type: string;
  amount: number;
  currency: string;
  date: string;
  investors?: any[];
}

export interface Stakeholder {
  user_id: string;
  name: string;
  email: string;
  avatar_url?: string;
  role: string;
}

export interface IncubationDashboard {
  project_id: string;
  updates: ProjectUpdate[];
  documents: ProjectDocument[];
  funding_rounds: ProjectFunding[];
  stakeholders: Stakeholder[];
}

export const incubationApi = {
  getDashboard: async (projectId: string): Promise<IncubationDashboard> => {
    const response = await api.get(`/projects/${projectId}/incubation/dashboard`);
    return response as any as IncubationDashboard;
  },

  createUpdate: async (projectId: string, data: Partial<ProjectUpdate>): Promise<ProjectUpdate> => {
    const response = await api.post(`/projects/${projectId}/incubation/updates`, data);
    return response as any as ProjectUpdate;
  },

  createDocument: async (projectId: string, data: Partial<ProjectDocument>): Promise<ProjectDocument> => {
    const response = await api.post(`/projects/${projectId}/incubation/documents`, data);
    return response as any as ProjectDocument;
  },

  createFundingRound: async (projectId: string, data: Partial<ProjectFunding>): Promise<ProjectFunding> => {
    const response = await api.post(`/projects/${projectId}/incubation/funding`, data);
    return response as any as ProjectFunding;
  },

  addStakeholder: async (projectId: string, userId: string, role: string): Promise<void> => {
    const params = new URLSearchParams({ user_id: userId, role });
    await api.post(`/projects/${projectId}/incubation/stakeholders?${params.toString()}`, null);
  }
};
