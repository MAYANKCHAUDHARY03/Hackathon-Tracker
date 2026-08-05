import { apiClient } from '@/lib/api-client';

export interface HackathonRound {
  id: string;
  hackathon_id: string;
  name: string;
  description?: string;
  round_type: string;
  sequence: number;
  status: string;
  starts_at?: string;
  ends_at?: string;
  result_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Deadline {
  id: string;
  hackathon_id: string;
  round_id?: string;
  name: string;
  description?: string;
  deadline_type: string;
  due_at: string;
  is_hard_deadline: boolean;
  source_url?: string;
  created_at: string;
  updated_at: string;
}

export const roundApi = {
  getRounds: (hackathonId: string) => 
    apiClient.get<HackathonRound[]>(`/hackathons/${hackathonId}/rounds`),
    
  createRound: (hackathonId: string, data: Partial<HackathonRound>) =>
    apiClient.post<HackathonRound>(`/hackathons/${hackathonId}/rounds`, data),
    
  getDeadlines: (hackathonId: string) =>
    apiClient.get<Deadline[]>(`/hackathons/${hackathonId}/rounds/deadlines`),
    
  createDeadline: (hackathonId: string, data: Partial<Deadline>) =>
    apiClient.post<Deadline>(`/hackathons/${hackathonId}/rounds/deadlines`, data),
};
