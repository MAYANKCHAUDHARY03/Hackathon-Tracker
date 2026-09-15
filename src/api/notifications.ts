import { apiClient as api } from "@/lib/api-client";

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  link?: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationPreference {
  category: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
  push_enabled: boolean;
  webhook_enabled: boolean;
}

export const notificationsApi = {
  getNotifications: (workspaceId: string, skip: number = 0, limit: number = 50) =>
    api.get<Notification[]>(`/workspaces/${workspaceId}/notifications?skip=${skip}&limit=${limit}`),
    
  getUnreadCount: (workspaceId: string) =>
    api.get<{ count: number }>(`/workspaces/${workspaceId}/notifications/unread/count`),

  markAsRead: (workspaceId: string, notificationId: string) =>
    api.post<Notification>(`/workspaces/${workspaceId}/notifications/${notificationId}/read`, {}),

  markAllAsRead: (workspaceId: string) =>
    api.post<{ message: string }>(`/workspaces/${workspaceId}/notifications/read-all`, {}),

  getPreferences: (workspaceId: string) =>
    api.get<NotificationPreference[]>(`/workspaces/${workspaceId}/notification-preferences`),

  updatePreference: (workspaceId: string, category: string, data: Partial<NotificationPreference>) =>
    api.put<NotificationPreference>(`/workspaces/${workspaceId}/notification-preferences/${category}`, data),
};
