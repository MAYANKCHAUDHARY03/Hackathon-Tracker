import { apiClient } from '@/lib/api-client';

export interface SubmissionRequirement {
  id: string;
  round_id: string;
  title: string;
  description?: string;
  requirement_type: string;
  is_required: boolean;
  sequence: number;
  validation_rules?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SubmissionItem {
  id: string;
  submission_id: string;
  requirement_id: string;
  content?: string;
  is_valid: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoundSubmission {
  id: string;
  hackathon_id: string;
  round_id: string;
  team_id: string;
  status: string;
  snapshot?: Record<string, any>;
  submitted_at?: string;
  locked_at?: string;
  locked_by?: string;
  created_at: string;
  updated_at: string;
  items: SubmissionItem[];
}

export const submissionApi = {
  getRequirements: (hackathonId: string, roundId: string) => 
    apiClient.get<SubmissionRequirement[]>(`/hackathons/${hackathonId}/rounds/${roundId}/requirements`),
    
  createRequirement: (hackathonId: string, roundId: string, data: Partial<SubmissionRequirement>) =>
    apiClient.post<SubmissionRequirement>(`/hackathons/${hackathonId}/rounds/${roundId}/requirements`, data),
    
  getSubmission: (hackathonId: string, roundId: string, teamId: string) =>
    apiClient.get<RoundSubmission>(`/hackathons/${hackathonId}/rounds/${roundId}/teams/${teamId}/submission`),
    
  updateItem: (hackathonId: string, roundId: string, teamId: string, data: { requirement_id: string; content: string }) =>
    apiClient.post<SubmissionItem>(`/hackathons/${hackathonId}/rounds/${roundId}/teams/${teamId}/submission/items`, data),

  lockSubmission: (hackathonId: string, roundId: string, teamId: string) =>
    apiClient.post<RoundSubmission>(`/hackathons/${hackathonId}/rounds/${roundId}/teams/${teamId}/submission/lock`, {}),
};
