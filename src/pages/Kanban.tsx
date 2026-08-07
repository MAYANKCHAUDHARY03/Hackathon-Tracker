import { useState, useEffect } from 'react';
import { KanbanBoard } from '@/components/kanban/KanbanBoard';
import { ActivityFeed } from '@/components/activity/ActivityFeed';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Brain } from 'lucide-react';
import { AIInsightsModal } from '@/components/kanban/AIInsightsModal';

interface Project {
  id: string;
  name: string;
}

export default function KanbanPage() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);

  useEffect(() => {
    async function loadProjects() {
      if (!activeWorkspaceId) return;
      setIsLoading(true);
      try {
        const data = await apiClient.get<Project[]>(`/workspaces/${activeWorkspaceId}/projects`);
        setProjects(data);
        if (data.length > 0) {
          setSelectedProjectId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load projects", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadProjects();
  }, [activeWorkspaceId]);

  if (isLoading) {
    return <div className="p-8">Loading projects...</div>;
  }

  if (projects.length === 0) {
    return (
      <div className="p-8 flex flex-col items-center justify-center h-full">
        <h2 className="text-xl font-semibold mb-2">No Projects Found</h2>
        <p className="text-muted-foreground">You need to create a project first to use the Kanban board.</p>
        {/* We would have a button to create a project here, but the projects page is a placeholder */}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-6 pb-0 flex items-center justify-between border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <label className="text-sm font-medium text-muted-foreground">Select Project:</label>
          <select 
            className="p-2 border border-border rounded-md bg-background text-foreground"
            value={selectedProjectId || ''}
            onChange={(e) => setSelectedProjectId(e.target.value)}
          >
            {projects.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
        
        {selectedProjectId && (
          <Button 
            variant="outline" 
            className="mb-4 gap-2 border-primary/20 bg-primary/5 hover:bg-primary/10 text-primary"
            onClick={() => setIsAIModalOpen(true)}
          >
            <Brain className="h-4 w-4" />
            AI Insights
          </Button>
        )}
      </div>
      <div className="flex-1 overflow-hidden flex">
        <div className="flex-1 overflow-hidden">
          {selectedProjectId && <KanbanBoard projectId={selectedProjectId} />}
        </div>
        {selectedProjectId && <ActivityFeed projectId={selectedProjectId} />}
      </div>
      
      {selectedProjectId && (
        <AIInsightsModal
          projectId={selectedProjectId}
          isOpen={isAIModalOpen}
          onClose={() => setIsAIModalOpen(false)}
        />
      )}
    </div>
  );
}
