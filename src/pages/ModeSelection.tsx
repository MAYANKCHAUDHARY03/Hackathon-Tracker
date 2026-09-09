import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/lib/api-client';
import { useAuthStore } from '@/store/authStore';
import { useWorkspaceStore } from '@/store/workspaceStore';
import type { AppMode } from '@/store/workspaceStore';
import type { Workspace } from '@/types';
import { UserCircle, Building2, AlertCircle, LogOut } from 'lucide-react';

export default function ModeSelection() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const { setApplicationMode, setActiveWorkspace, syncWithUser } = useWorkspaceStore();
  
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchWorkspaces = async () => {
      try {
        const data = await apiClient.get<Workspace[]>('/workspaces');
        setWorkspaces(data);
      } catch (err) {
        console.error("Failed to load workspaces", err);
        setError("Failed to load your workspaces. Please try refreshing.");
      } finally {
        setLoading(false);
      }
    };
    fetchWorkspaces();
  }, []);

  const handleModeSelection = (mode: AppMode) => {
    if (!user) return;
    
    let validWorkspaces: Workspace[] = [];
    if (mode === 'student') {
      validWorkspaces = workspaces.filter(w => !w.organization_id);
    } else {
      validWorkspaces = workspaces.filter(w => w.organization_id);
    }

    if (validWorkspaces.length === 0) {
      setError(`You do not have access to any ${mode} workspaces.`);
      return;
    }

    setApplicationMode(mode, user.id);
    setActiveWorkspace(validWorkspaces[0].id, user.id);
    navigate('/');
  };

  const handleLogout = () => {
    logout();
    syncWithUser(null);
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50/50 backdrop-blur-sm">
        <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4 sm:p-8">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-indigo-300/20 blur-3xl mix-blend-multiply" />
        <div className="absolute top-[60%] -right-[10%] w-[40%] h-[60%] rounded-full bg-purple-300/20 blur-3xl mix-blend-multiply" />
      </div>

      <div className="relative z-10 w-full max-w-4xl">
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
            Welcome back, {user?.full_name?.split(' ')[0] || 'User'}
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            How do you want to use Hackathon Tracker today?
          </p>
        </div>

        {error && (
          <div className="mx-auto mb-8 max-w-2xl rounded-xl border border-red-200 bg-red-50/50 p-4 text-center text-sm text-red-600 backdrop-blur flex items-center justify-center gap-2 shadow-sm">
            <AlertCircle className="h-5 w-5" />
            {error}
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-2 md:gap-8">
          <button
            onClick={() => handleModeSelection('student')}
            className="group relative flex flex-col items-center justify-center overflow-hidden rounded-3xl border border-white/40 bg-white/60 p-10 text-center shadow-lg backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:border-indigo-200 hover:bg-white/80 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-indigo-500/20"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 transition-opacity group-hover:opacity-100" />
            <div className="relative mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 shadow-inner transition-transform duration-300 group-hover:scale-110">
              <UserCircle className="h-12 w-12" />
            </div>
            <h3 className="relative text-2xl font-bold text-gray-900">Student / Participant</h3>
            <p className="relative mt-4 text-gray-500 leading-relaxed">
              Participate in hackathons, manage your teams, work on projects, and submit your work.
            </p>
          </button>

          <button
            onClick={() => handleModeSelection('organization')}
            className="group relative flex flex-col items-center justify-center overflow-hidden rounded-3xl border border-white/40 bg-white/60 p-10 text-center shadow-lg backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:border-purple-200 hover:bg-white/80 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-purple-500/20"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 opacity-0 transition-opacity group-hover:opacity-100" />
            <div className="relative mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-purple-100 text-purple-600 shadow-inner transition-transform duration-300 group-hover:scale-110">
              <Building2 className="h-12 w-12" />
            </div>
            <h3 className="relative text-2xl font-bold text-gray-900">Organization</h3>
            <p className="relative mt-4 text-gray-500 leading-relaxed">
              Manage hackathons, oversee participants, coordinate mentors and judges, and review results.
            </p>
          </button>
        </div>
        
        <div className="mt-12 text-center">
          <button 
            onClick={handleLogout}
            className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
