import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { projectsApi } from '@/api/projectsApi';
import type { Project } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { FolderGit2, Calendar, GitBranch, ArrowRight } from 'lucide-react';
import { format } from 'date-fns';

export default function Projects() {
  const navigate = useNavigate();
  const { activeWorkspaceId } = useWorkspaceStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchProjects() {
      if (!activeWorkspaceId) return;
      setIsLoading(true);
      setError(null);
      try {
        const data = await projectsApi.getProjects(activeWorkspaceId);
        setProjects(data);
      } catch (err: any) {
        setError(err instanceof Error ? err : new Error('Failed to load projects'));
      } finally {
        setIsLoading(false);
      }
    }
    fetchProjects();
  }, [activeWorkspaceId]);

  if (!activeWorkspaceId) {
    return <div className="p-8">Please select a workspace first.</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Project Database</h1>
          <p className="text-muted-foreground mt-1">Explore projects submitted across the workspace.</p>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map(i => (
            <GlassPanel key={i} className="h-48 animate-pulse bg-secondary/20" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center p-8 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
          <p>{error.message}</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-12">
          <div className="p-4 bg-primary/10 text-primary rounded-full w-16 h-16 mx-auto flex items-center justify-center mb-4">
            <FolderGit2 className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-semibold mb-2">No projects found</h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Projects will appear here once teams create submissions.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map(project => (
            <GlassPanel 
              key={project.id} 
              className="p-6 flex flex-col hover:border-primary/50 transition-all cursor-pointer group hover:shadow-md"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold truncate pr-4 group-hover:text-primary transition-colors">
                  {project.name}
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-secondary text-secondary-foreground px-2 py-1 rounded">
                  {project.status || 'Active'}
                </span>
              </div>
              
              <p className="text-sm text-muted-foreground line-clamp-3 mb-6 flex-1">
                {project.description || 'No description provided.'}
              </p>
              
              <div className="space-y-2 mb-4">
                {project.repo_url && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <GitBranch className="h-4 w-4" />
                    <span className="truncate">{new URL(project.repo_url).hostname}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Updated {format(new Date(project.updated_at), 'MMM d, yyyy')}</span>
                </div>
              </div>
              
              <div className="mt-auto pt-4 border-t border-border/50 flex items-center justify-between text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                <span>View Details</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
