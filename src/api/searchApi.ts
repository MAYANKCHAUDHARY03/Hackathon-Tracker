import { apiClient as api } from "@/lib/api-client";

export interface SearchResultItem {
  id: string;
  type: string;
  title: string;
  description?: string;
  url: string;
  created_at: string;
  metadata: Record<string, any>;
  graph_context?: Record<string, string[]>;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
  total: number;
}

export const searchApi = {
  search: (workspaceId: string, query: string) =>
    api.get<SearchResponse>(`/workspaces/${workspaceId}/search?q=${encodeURIComponent(query)}`),
};
