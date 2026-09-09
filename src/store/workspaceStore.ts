import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ID } from '@/types';

export type AppMode = 'student' | 'organization';

interface WorkspaceState {
  activeWorkspaceId: ID | null;
  applicationMode: AppMode | null;
  userWorkspaces: Record<ID, ID>;
  userModes: Record<ID, AppMode>;
  
  setActiveWorkspace: (id: ID, userId?: ID) => void;
  setApplicationMode: (mode: AppMode, userId?: ID) => void;
  clearActiveWorkspace: () => void;
  syncWithUser: (userId: ID | null) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set, get) => ({
      activeWorkspaceId: null,
      applicationMode: null,
      userWorkspaces: {},
      userModes: {},
      
      setActiveWorkspace: (id, userId) => set((state) => ({
        activeWorkspaceId: id,
        userWorkspaces: userId ? { ...state.userWorkspaces, [userId]: id } : state.userWorkspaces
      })),
      
      setApplicationMode: (mode, userId) => set((state) => ({
        applicationMode: mode,
        userModes: userId ? { ...state.userModes, [userId]: mode } : state.userModes
      })),
      
      clearActiveWorkspace: () => set({ activeWorkspaceId: null, applicationMode: null }),
      
      syncWithUser: (userId) => {
        if (!userId) {
          set({ activeWorkspaceId: null, applicationMode: null });
          return;
        }
        const state = get();
        set({
          activeWorkspaceId: state.userWorkspaces[userId] || null,
          applicationMode: state.userModes[userId] || null
        });
      }
    }),
    {
      name: 'ht-workspace-storage',
    }
  )
);
