import { apiClient } from '../lib/api-client';

export interface WebhookSubscription {
  id: string;
  workspace_id: string;
  url: string;
  events: string[];
  secret?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WebhookSubscriptionCreate {
  url: string;
  events: string[];
  secret?: string;
  is_active?: boolean;
}

export interface WebhookDelivery {
  id: string;
  subscription_id: string;
  event_type: string;
  payload: any;
  status_code?: number;
  response_body?: string;
  created_at: string;
}

export const webhookApi = {
  listSubscriptions: async (workspaceId: string): Promise<WebhookSubscription[]> => {
    return await apiClient.get<WebhookSubscription[]>(`/workspaces/${workspaceId}/webhooks`);
  },

  createSubscription: async (workspaceId: string, subscription: WebhookSubscriptionCreate): Promise<WebhookSubscription> => {
    return await apiClient.post<WebhookSubscription>(`/workspaces/${workspaceId}/webhooks`, subscription);
  },

  listDeliveries: async (workspaceId: string, subscriptionId: string): Promise<WebhookDelivery[]> => {
    return await apiClient.get<WebhookDelivery[]>(`/workspaces/${workspaceId}/webhooks/${subscriptionId}/deliveries`);
  },
};
