import { apiClient as api } from "@/lib/api-client";

export interface Person {
  id: string;
  workspace_id: string;
  first_name: string;
  last_name: string;
  email: string;
  bio?: string;
  avatar_url?: string;
  linkedin_url?: string;
}

export interface MentorAssignment {
  id: string;
  mentor_id: string;
  hackathon_id: string;
  round_id?: string;
  team_id?: string;
  expertise_areas?: string[];
  status: string;
}

export interface JudgeAssignment {
  id: string;
  judge_id: string;
  hackathon_id: string;
  round_id?: string;
  status: string;
}

export interface CsvImportResult {
  total_processed: int;
  successful: int;
  failed: int;
  errors: string[];
}

export const peopleApi = {
  getPeople: (workspaceId: string) =>
    api.get<Person[]>(`/workspaces/${workspaceId}/people`),

  createPerson: (workspaceId: string, data: Partial<Person>) =>
    api.post<Person>(`/workspaces/${workspaceId}/people`, data),

  getMentorAssignments: (workspaceId: string, hackathonId: string) =>
    api.get<MentorAssignment[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/mentors`),

  assignMentor: (workspaceId: string, hackathonId: string, data: Partial<MentorAssignment>) =>
    api.post<MentorAssignment>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/mentors`, data),

  getJudgeAssignments: (workspaceId: string, hackathonId: string) =>
    api.get<JudgeAssignment[]>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/judges`),

  assignJudge: (workspaceId: string, hackathonId: string, data: Partial<JudgeAssignment>) =>
    api.post<JudgeAssignment>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/judges`, data),

  importPeopleCsv: (workspaceId: string, hackathonId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<CsvImportResult>(`/workspaces/${workspaceId}/hackathons/${hackathonId}/people/import`, formData);
  }
};
