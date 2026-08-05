import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface FilterState {
  globalSearch: string;
  hackathonStatus: string[];
  setGlobalSearch: (query: string) => void;
  setHackathonStatus: (statuses: string[]) => void;
  clearFilters: () => void;
}

export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      globalSearch: '',
      hackathonStatus: [],
      setGlobalSearch: (query) => set({ globalSearch: query }),
      setHackathonStatus: (statuses) => set({ hackathonStatus: statuses }),
      clearFilters: () => set({ globalSearch: '', hackathonStatus: [] }),
    }),
    {
      name: 'ht-filter-storage',
    }
  )
);
