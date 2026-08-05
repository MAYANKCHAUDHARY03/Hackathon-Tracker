import { apiClient as api } from "@/lib/api-client";

export interface EvaluationCriterion {
  id: string;
  name: string;
  description?: string;
  weight: number;
  max_score: number;
}

export interface EvaluationTemplate {
  id: string;
  hackathon_id: string;
  name: string;
  description?: string;
  criteria: EvaluationCriterion[];
}

export interface EvaluationScore {
  id: string;
  criterion_id: string;
  score: number;
  notes?: string;
  criterion_name_snapshot: string;
  criterion_weight_snapshot: number;
  criterion_max_score_snapshot: number;
}

export interface Evaluation {
  id: string;
  hackathon_id: string;
  round_id: string;
  team_id: string;
  project_id?: string;
  judge_id: string;
  template_id?: string;
  status: string;
  overall_score?: number;
  overall_feedback?: string;
  scores: EvaluationScore[];
}

export const evaluationsApi = {
  getTemplates: (workspaceId: string, hackathonId: string) =>
    api.get<EvaluationTemplate[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/evaluation-templates`),

  createTemplate: (workspaceId: string, hackathonId: string, data: Partial<EvaluationTemplate>) =>
    api.post<EvaluationTemplate>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/evaluation-templates`, data),

  createCriterion: (workspaceId: string, hackathonId: string, templateId: string, data: Partial<EvaluationCriterion>) =>
    api.post<EvaluationCriterion>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/evaluation-templates/${templateId}/criteria`, data),

  createEvaluation: (workspaceId: string, hackathonId: string, data: Partial<Evaluation>) =>
    api.post<Evaluation>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/evaluations`, data),

  updateEvaluation: (workspaceId: string, hackathonId: string, evaluationId: string, data: Partial<Evaluation>) =>
    api.put<Evaluation>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/evaluations/${evaluationId}`, data),
};
