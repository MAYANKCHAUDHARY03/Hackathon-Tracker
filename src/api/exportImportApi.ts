import { apiClient as api } from "@/lib/api-client";

export interface WorkspaceExport {
  version: string;
  workspace: Record<string, any>;
  hackathons: Record<string, any>[];
  projects: Record<string, any>[];
  teams: Record<string, any>[];
}

export interface ImportPreviewResponse {
  is_valid: boolean;
  hackathons_count: number;
  projects_count: number;
  teams_count: number;
  errors: string[];
}

export const exportImportApi = {
  exportWorkspace: (workspaceId: string) =>
    api.get<WorkspaceExport>(`/workspaces/${workspaceId}/export`),
    
  previewImport: (workspaceId: string, data: WorkspaceExport) =>
    api.post<ImportPreviewResponse>(`/workspaces/${workspaceId}/import/preview`, data),
    
  executeImport: (workspaceId: string, data: WorkspaceExport, overwrite: boolean = false) =>
    api.post<{success: boolean}>(`/workspaces/${workspaceId}/import/execute`, { data, overwrite }),
};
