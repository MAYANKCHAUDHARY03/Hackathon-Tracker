import { useState, useCallback, useEffect } from 'react';
import { kanbanApi, type KanbanBoard } from '@/api/kanbanApi';
import { useWorkspaceStore } from '@/store/workspaceStore';

export function useKanban(projectId: string | undefined) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [board, setBoard] = useState<KanbanBoard | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchBoard = useCallback(async () => {
    if (!activeWorkspaceId || !projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await kanbanApi.getBoard(activeWorkspaceId, projectId);
      setBoard(data);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error('Failed to load board'));
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspaceId, projectId]);

  useEffect(() => {
    fetchBoard();
  }, [fetchBoard]);

  const moveTask = async (taskId: string, sourceColId: string, destColId: string, newPosition: number) => {
    if (!board || !activeWorkspaceId) return;

    // Optimistic update
    setBoard((prev) => {
      if (!prev) return prev;
      const newBoard = { ...prev };
      const sourceCol = newBoard.columns.find(c => c.id === sourceColId);
      const destCol = newBoard.columns.find(c => c.id === destColId);
      if (!sourceCol || !destCol) return prev;

      const taskIndex = sourceCol.tasks.findIndex(t => t.id === taskId);
      if (taskIndex === -1) return prev;

      const [task] = sourceCol.tasks.splice(taskIndex, 1);
      task.column_id = destColId;
      task.position = newPosition;
      
      destCol.tasks.push(task);
      destCol.tasks.sort((a, b) => a.position - b.position);
      
      return newBoard;
    });

    try {
      await kanbanApi.updateTask(activeWorkspaceId, taskId, {
        column_id: destColId,
        position: newPosition
      });
    } catch (error) {
      // Revert on failure
      fetchBoard();
    }
  };

  const createTask = async (columnId: string, title: string, description?: string) => {
    if (!activeWorkspaceId) return;
    const newTask = await kanbanApi.createTask(activeWorkspaceId, columnId, { title, description });
    setBoard(prev => {
      if (!prev) return prev;
      const newBoard = { ...prev };
      const col = newBoard.columns.find(c => c.id === columnId);
      if (col) {
        col.tasks.push(newTask);
        col.tasks.sort((a, b) => a.position - b.position);
      }
      return newBoard;
    });
  };

  const updateTask = async (taskId: string, columnId: string, updates: { title?: string; description?: string }) => {
    if (!activeWorkspaceId) return;
    const updated = await kanbanApi.updateTask(activeWorkspaceId, taskId, updates);
    setBoard(prev => {
      if (!prev) return prev;
      const newBoard = { ...prev };
      const col = newBoard.columns.find(c => c.id === columnId);
      if (col) {
        const idx = col.tasks.findIndex(t => t.id === taskId);
        if (idx !== -1) {
          col.tasks[idx] = { ...col.tasks[idx], ...updated };
        }
      }
      return newBoard;
    });
  };

  return {
    board,
    isLoading,
    error,
    moveTask,
    createTask,
    updateTask,
    refetch: fetchBoard
  };
}
