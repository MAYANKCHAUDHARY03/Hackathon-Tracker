import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import type { DashboardSummaryResponse } from '@/types/dashboard';

export function useDashboard() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [data, setData] = useState<DashboardSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDashboard = useCallback(async () => {
    if (!activeWorkspaceId) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await apiClient.get<DashboardSummaryResponse>(`/workspaces/${activeWorkspaceId}/dashboard`);
      setData(result);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error(err?.message || 'Failed to load dashboard summary'));
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspaceId]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchDashboard
  };
}
