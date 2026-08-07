import { apiClient } from '@/lib/api-client'

export type FeedbackType = 'Bug' | 'Friction' | 'Request'

export interface FeedbackCreate {
  type: FeedbackType
  description: string
  url?: string
}

export interface FeedbackResponse extends FeedbackCreate {
  id: string
  user_id?: string
  created_at: string
  updated_at: string
}

export const feedbackApi = {
  createFeedback: (data: FeedbackCreate) => 
    apiClient.post<FeedbackResponse>('/feedback', data),
    
  getFeedback: () => 
    apiClient.get<FeedbackResponse[]>('/feedback'),
}
