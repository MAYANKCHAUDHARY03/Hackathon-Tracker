import { apiClient } from '@/lib/api-client';

export interface KanbanTask {
  id: string;
  column_id: string;
  title: string;
  description?: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface KanbanColumn {
  id: string;
  board_id: string;
  name: string;
  position: number;
  tasks: KanbanTask[];
  created_at: string;
  updated_at: string;
}

export interface KanbanBoard {
  id: string;
  project_id: string;
  name: string;
  columns: KanbanColumn[];
  created_at: string;
  updated_at: string;
}

export const kanbanApi = {
  getBoard: (workspaceId: string, projectId: string) => 
    apiClient.get<KanbanBoard>(`/workspaces/${workspaceId}/projects/${projectId}/kanban`),
    
  createColumn: (workspaceId: string, boardId: string, name: string) =>
    apiClient.post<KanbanColumn>(`/workspaces/${workspaceId}/kanban/boards/${boardId}/columns`, { name }),
    
  updateColumn: (workspaceId: string, columnId: string, updates: { name?: string; position?: number }) =>
    apiClient.patch<KanbanColumn>(`/workspaces/${workspaceId}/kanban/columns/${columnId}`, updates),
    
  createTask: (workspaceId: string, columnId: string, data: { title: string; description?: string }) =>
    apiClient.post<KanbanTask>(`/workspaces/${workspaceId}/kanban/columns/${columnId}/tasks`, data),
    
  updateTask: (workspaceId: string, taskId: string, updates: { title?: string; description?: string; column_id?: string; position?: number }) =>
    apiClient.patch<KanbanTask>(`/workspaces/${workspaceId}/kanban/tasks/${taskId}`, updates),
};
