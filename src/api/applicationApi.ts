import { api } from './api';

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
    const response = await api.post(`/hackathons/${hackathonId}/forms`, form);
    return response.data;
  },

  listForms: async (hackathonId: string): Promise<ApplicationForm[]> => {
    const response = await api.get(`/hackathons/${hackathonId}/forms`);
    return response.data;
  },

  getForm: async (formId: string): Promise<ApplicationForm> => {
    const response = await api.get(`/forms/${formId}`);
    return response.data;
  },

  submitApplication: async (formId: string, submission: ApplicationSubmissionCreate): Promise<ApplicationSubmission> => {
    const response = await api.post(`/forms/${formId}/submissions`, submission);
    return response.data;
  },

  listSubmissions: async (hackathonId: string): Promise<ApplicationSubmission[]> => {
    const response = await api.get(`/hackathons/${hackathonId}/submissions`);
    return response.data;
  },

  updateSubmissionStatus: async (submissionId: string, status: 'pending' | 'approved' | 'rejected'): Promise<ApplicationSubmission> => {
    const response = await api.patch(`/submissions/${submissionId}/status`, { status });
    return response.data;
  }
};
