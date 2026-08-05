import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, ChevronDown } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import type { Workspace } from '@/types';

export function WorkspaceSwitcher() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const { activeWorkspaceId, setActiveWorkspace } = useWorkspaceStore();
  const navigate = useNavigate();

  useEffect(() => {
    async function loadWorkspaces() {
      try {
        const data = await apiClient.get<Workspace[]>('/workspaces');
        setWorkspaces(data);
        if (data.length > 0 && !activeWorkspaceId) {
          setActiveWorkspace(data[0].id);
        }
      } catch (err) {
        console.error('Failed to load workspaces', err);
      }
    }
    loadWorkspaces();
  }, [activeWorkspaceId, setActiveWorkspace]);

  const handleWorkspaceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    if (id === 'new') {
      // For now just alert, could open a modal
      alert("Feature: Create New Workspace");
      e.target.value = activeWorkspaceId || '';
      return;
    }
    setActiveWorkspace(id);
    navigate('/'); // Refresh dashboard
  };

  return (
    <div className="relative inline-flex items-center">
      <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">
        <Building2 className="h-4 w-4" />
      </div>
      <select
        value={activeWorkspaceId || ''}
        onChange={handleWorkspaceChange}
        className="h-10 w-48 appearance-none rounded-md bg-secondary/30 pl-9 pr-8 text-sm font-medium border border-border/50 outline-none focus:ring-2 focus:ring-primary/50 text-foreground cursor-pointer transition-colors hover:bg-secondary/50"
      >
        <option value="" disabled>Select Workspace...</option>
        {workspaces.map(w => (
          <option key={w.id} value={w.id}>
            {w.name}
          </option>
        ))}
        {/* <option value="new">+ Create Workspace</option> */}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">
        <ChevronDown className="h-4 w-4" />
      </div>
    </div>
  );
}
