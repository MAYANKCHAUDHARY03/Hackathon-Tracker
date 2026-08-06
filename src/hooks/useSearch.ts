import { useQuery } from '@tanstack/react-query';
import { searchApi } from '@/api/searchApi';
import type { SearchResponse } from '@/api/searchApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { useDebounce } from '@/hooks/useDebounce';

export function useSearch(query: string) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const debouncedQuery = useDebounce(query, 300);

  return useQuery<SearchResponse, Error>({
    queryKey: ['search', activeWorkspaceId, debouncedQuery],
    queryFn: async () => {
      if (!activeWorkspaceId || debouncedQuery.length < 2) {
        return { query: debouncedQuery, results: [], total: 0 };
      }
      const response = await searchApi.search(activeWorkspaceId, debouncedQuery);
      return response;
    },
    enabled: !!activeWorkspaceId && debouncedQuery.length >= 2,
    staleTime: 1000 * 60, // 1 minute
  });
}
