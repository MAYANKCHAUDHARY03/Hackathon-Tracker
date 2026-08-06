import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/api/analyticsApi';
import type { WorkspaceAnalyticsSummary } from '@/api/analyticsApi';
import { useWorkspaceStore } from '@/store/workspaceStore';

export function useAnalytics() {
  const { activeWorkspaceId } = useWorkspaceStore();

  return useQuery<WorkspaceAnalyticsSummary, Error>({
    queryKey: ['analytics', activeWorkspaceId],
    queryFn: async () => {
      if (!activeWorkspaceId) throw new Error('No active workspace');
      const response = await analyticsApi.getWorkspaceAnalytics(activeWorkspaceId);
      return response;
    },
    enabled: !!activeWorkspaceId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
