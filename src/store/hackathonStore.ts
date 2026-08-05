import { create } from 'zustand';
import type { Hackathon, NormalizedState, ID } from '@/types';

interface HackathonState {
  hackathons: NormalizedState<Hackathon>;
  
  // Actions
  addHackathon: (hackathon: Hackathon) => void;
  updateHackathon: (id: ID, data: Partial<Hackathon>) => void;
  deleteHackathon: (id: ID) => void;
}

export const useHackathonStore = create<HackathonState>((set) => ({
  hackathons: { byId: {}, allIds: [] },

  addHackathon: (hackathon) => set((state) => {
    if (state.hackathons.byId[hackathon.id]) return state; // Avoid duplicate
    return {
      hackathons: {
        byId: { ...state.hackathons.byId, [hackathon.id]: hackathon },
        allIds: [...state.hackathons.allIds, hackathon.id],
      }
    };
  }),

  updateHackathon: (id, data) => set((state) => {
    if (!state.hackathons.byId[id]) return state;
    return {
      hackathons: {
        ...state.hackathons,
        byId: {
          ...state.hackathons.byId,
          [id]: { ...state.hackathons.byId[id], ...data, updated_at: new Date().toISOString() }
        }
      }
    };
  }),

  deleteHackathon: (id) => set((state) => {
    if (!state.hackathons.byId[id]) return state;
    // Soft delete
    return {
      hackathons: {
        ...state.hackathons,
        byId: {
          ...state.hackathons.byId,
          [id]: { ...state.hackathons.byId[id], deleted_at: new Date().toISOString() }
        }
      }
    };
  }),
}));
