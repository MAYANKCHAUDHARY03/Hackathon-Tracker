import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import type { User } from '@/types';

interface BootSequenceProps {
  children: React.ReactNode;
}

export const BootSequence: React.FC<BootSequenceProps> = ({ children }) => {
  const [isInitializing, setIsInitializing] = useState(true);
  const { token, isAuthenticated, setUser, logout } = useAuthStore();
  const { syncWithUser } = useWorkspaceStore();

  useEffect(() => {
    const initializeApp = async () => {
      if (!token) {
        if (isAuthenticated) {
          logout();
        }
        syncWithUser(null);
        setIsInitializing(false);
        return;
      }

      try {
        const user = await apiClient.get<User>('/users/me');
        setUser(user);
        syncWithUser(user.id);
        setIsInitializing(false);
      } catch (error) {
        console.error('Failed to initialize session:', error);
        logout();
        syncWithUser(null);
        setIsInitializing(false);
      }
    };

    initializeApp();
  }, [token, isAuthenticated, setUser, logout, syncWithUser]);

  if (isInitializing) {
    return (
      <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/95 backdrop-blur-md transition-opacity duration-500">
        <div className="relative flex items-center justify-center">
          <div className="absolute h-32 w-32 animate-ping rounded-full bg-primary/20" />
          <div className="z-10 flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-primary/80 shadow-2xl border border-white/10 backdrop-blur-lg">
            <svg 
              className="h-12 w-12 text-primary-foreground animate-pulse" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
        <h2 className="mt-8 text-2xl font-bold tracking-tight text-foreground/80 animate-pulse">
          Initializing Workspace...
        </h2>
      </div>
    );
  }

  return <>{children}</>;
};
