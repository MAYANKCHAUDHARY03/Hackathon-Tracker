import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ID } from '@/types';

interface WorkspaceState {
  activeWorkspaceId: ID | null;
  setActiveWorkspace: (id: ID) => void;
  clearActiveWorkspace: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      activeWorkspaceId: null,
      setActiveWorkspace: (id) => set({ activeWorkspaceId: id }),
      clearActiveWorkspace: () => set({ activeWorkspaceId: null }),
    }),
    {
      name: 'ht-workspace-storage',
    }
  )
);
