import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useWorkspaceStore } from '@/store/workspaceStore';

export const ProtectedRoute: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const applicationMode = useWorkspaceStore((state) => state.applicationMode);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname + location.search)}`} replace />;
  }

  // Redirect to mode-selection if no applicationMode is set
  // Ensure we don't cause an infinite loop if they are already on /mode-selection
  if (!applicationMode && location.pathname !== '/mode-selection') {
    return <Navigate to="/mode-selection" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};
