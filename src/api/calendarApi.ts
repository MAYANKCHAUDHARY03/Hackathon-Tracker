import { apiClient as api } from "@/lib/api-client";

export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  event_type: string;
  date: string;
  hackathon_id: string;
  hackathon_name: string;
  color: string;
  is_hard_deadline: boolean;
}

export const calendarApi = {
  getEvents: (workspaceId: string, start: string, end: string) =>
    api.get<CalendarEvent[]>(
      `/workspaces/${workspaceId}/calendar?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`
    ),
};
