import { create } from 'zustand';

export interface HistoryAction {
  id: string;
  label: string;
  undo: () => void;
  redo: () => void;
}

interface HistoryState {
  past: HistoryAction[];
  future: HistoryAction[];
  
  pushAction: (action: Omit<HistoryAction, 'id'>) => void;
  undo: () => void;
  redo: () => void;
  clearHistory: () => void;
}

export const useHistoryStore = create<HistoryState>((set, get) => ({
  past: [],
  future: [],

  pushAction: (actionConfig) => {
    const newAction: HistoryAction = {
      ...actionConfig,
      id: crypto.randomUUID(),
    };
    
    set((state) => ({
      past: [...state.past, newAction],
      future: [], // Clear future on new action
    }));
  },

  undo: () => {
    const { past, future } = get();
    if (past.length === 0) return;
    
    const previous = past[past.length - 1];
    const newPast = past.slice(0, past.length - 1);
    
    previous.undo();
    
    set({
      past: newPast,
      future: [previous, ...future],
    });
  },

  redo: () => {
    const { past, future } = get();
    if (future.length === 0) return;
    
    const next = future[0];
    const newFuture = future.slice(1);
    
    next.redo();
    
    set({
      past: [...past, next],
      future: newFuture,
    });
  },

  clearHistory: () => set({ past: [], future: [] }),
}));
