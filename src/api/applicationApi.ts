import { apiClient as api } from '@/lib/api-client';

export interface FormField {
  id: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'file';
  label: string;
  required: boolean;
  options?: string[]; // for select/radio
  description?: string;
}

export interface FormSchema {
  fields: FormField[];
}

export interface ApplicationForm {
  id: string;
  hackathon_id: string;
  title: string;
  description?: string;
  schema_json: FormSchema;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApplicationFormCreate {
  title: string;
  description?: string;
  schema_json: FormSchema;
  is_published: boolean;
}

export interface ApplicationSubmission {
  id: string;
  form_id: string;
  user_id?: string;
  data_json: Record<string, any>;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface ApplicationSubmissionCreate {
  data_json: Record<string, any>;
}

export const applicationApi = {
  createForm: async (hackathonId: string, form: ApplicationFormCreate): Promise<ApplicationForm> => {
    const response = await api.post<ApplicationForm>(`/hackathons/${hackathonId}/forms`, form);
    return response;
  },

  listForms: async (hackathonId: string): Promise<ApplicationForm[]> => {
    const response = await api.get<ApplicationForm[]>(`/hackathons/${hackathonId}/forms`);
    return response;
  },

  getForm: async (formId: string): Promise<ApplicationForm> => {
    const response = await api.get<ApplicationForm>(`/forms/${formId}`);
    return response;
  },

  submitApplication: async (formId: string, submission: ApplicationSubmissionCreate): Promise<ApplicationSubmission> => {
    const response = await api.post<ApplicationSubmission>(`/forms/${formId}/submissions`, submission);
    return response;
  },

  listSubmissions: async (hackathonId: string): Promise<ApplicationSubmission[]> => {
    const response = await api.get<ApplicationSubmission[]>(`/hackathons/${hackathonId}/submissions`);
    return response;
  },

  updateSubmissionStatus: async (submissionId: string, status: 'pending' | 'approved' | 'rejected'): Promise<ApplicationSubmission> => {
    const response = await api.patch<ApplicationSubmission>(`/submissions/${submissionId}/status`, { status });
    return response;
  }
};
